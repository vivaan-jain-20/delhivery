import os
import re
import pickle
import pandas as pd
import networkx as nx
import folium
import branca.colormap as cm

def load_coordinates():
    """
    Downloads and caches the Indian pincode coordinates dataset.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "pincodes_coordinates.csv")
    
    if not os.path.exists(csv_path):
        print("Downloading Indian pincode coordinates database...")
        url = "https://raw.githubusercontent.com/dropdevrahul/pincodes-india/main/pincode.csv"
        try:
            df = pd.read_csv(url, low_memory=False)
            
            # Standardize columns to lowercase and clean values
            df = df.rename(columns={
                'Pincode': 'pincode',
                'Latitude': 'latitude',
                'Longitude': 'longitude'
            })
            
            # Convert to numeric, coercing errors (like text headers or corrupt rows) to NaN
            df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # Keep only necessary columns and drop rows with NaN values
            df = df[['pincode', 'latitude', 'longitude']].dropna()
            
            # Group by pincode and average coordinates to ensure unique mapping
            df = df.groupby('pincode').mean().reset_index()
            
            df.to_csv(csv_path, index=False)
            return df
        except Exception as e:
            print(f"Warning: Failed to download coordinate database: {e}")
            return pd.DataFrame(columns=['pincode', 'latitude', 'longitude'])
    else:
        return pd.read_csv(csv_path)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    graph_pkl_path = os.path.join(current_dir, "delhivery_graph.pkl")
    output_file = os.path.join(current_dir, "..", "delhivery_geo_network.html")

    # 1. Load the Graph
    print(f"Loading NetworkX graph from: {graph_pkl_path}...")
    if not os.path.exists(graph_pkl_path):
        print(f"Error: Pickled graph not found at {graph_pkl_path}. Please run run_pipeline.py first.")
        return

    with open(graph_pkl_path, "rb") as f:
        G = pickle.load(f)
    print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # 2. Map coordinates to the nodes using pincode database
    pincode_df = load_coordinates()
    if not pincode_df.empty:
        # Create coordinates lookup dictionary: pincode -> (lat, lon)
        coords_dict = dict(zip(pincode_df['pincode'].astype(int), zip(pincode_df['latitude'], pincode_df['longitude'])))
        
        mapped_count = 0
        for node_id in G.nodes:
            # Extract 6-digit pincode from center ID (e.g. IND388121AAA -> 388121)
            match = re.search(r'\d{6}', str(node_id))
            if match:
                pincode = int(match.group(0))
                if pincode in coords_dict:
                    lat, lon = coords_dict[pincode]
                    G.nodes[node_id]['lat'] = lat
                    G.nodes[node_id]['lon'] = lon
                    mapped_count += 1
        print(f"Successfully mapped {mapped_count}/{G.number_of_nodes()} facility nodes to geographical coordinates.")
    else:
        print("Warning: Coordinate mapping skipped because database is empty or failed to load.")

    # 3. Calculate the Chokehold Metric (Betweenness Centrality)
    print("Calculating network centralities...")
    # Convert MultiDiGraph to DiGraph because betweenness centrality calculation 
    # doesn't natively support MultiDiGraphs.
    centrality = nx.betweenness_centrality(nx.DiGraph(G))
    nx.set_node_attributes(G, centrality, 'betweenness')

    # 4. Setup the Map & Color Gradients
    # Dark mode map makes heatmaps pop significantly better
    print("Initializing Folium map...")
    logistics_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='cartodbdark_matter')

    # Edge Color: Green (Fast) -> Yellow (Warning) -> Red (Severe Delay)
    delay_cmap = cm.LinearColormap(
        colors=['#00FF00', '#FFFF00', '#FF0000'], 
        index=[0.8, 1.1, 1.5], # Ratios: <1.1 is fine, >1.5 is terrible
        vmin=0.5, vmax=2.0,
        caption='Corridor Delay Ratio (Actual / OSRM)'
    )

    # Node Color: Blue (Low Bridge Risk) -> Purple (Massive Chokehold)
    vmin_c = min(centrality.values()) if centrality else 0.0
    vmax_c = max(centrality.values()) if centrality else 1.0
    # Safeguard against zero-division error in colormap bounds
    if vmin_c == vmax_c:
        vmax_c = vmin_c + 1e-6

    chokehold_cmap = cm.LinearColormap(
        colors=['#00BFFF', '#8A2BE2', '#FF1493'], 
        vmin=vmin_c, vmax=vmax_c,
        caption='Hub Betweenness Centrality (Chokehold Risk)'
    )

    logistics_map.add_child(delay_cmap)
    logistics_map.add_child(chokehold_cmap)

    # 5. Draw the Corridors (Edges) First so they sit under the hubs
    print("Rendering corridors...")
    rendered_edges = 0
    for source, dest, data in G.edges(data=True):
        # Ensure coordinates exist for both ends
        if 'lat' in G.nodes[source] and 'lat' in G.nodes[dest]:
            start_coords = [G.nodes[source]['lat'], G.nodes[source]['lon']]
            end_coords = [G.nodes[dest]['lat'], G.nodes[dest]['lon']]
            
            delay = data.get('median_delay_ratio', 1.0)
            trips = data.get('total_trips', 1)
            
            # Edge thickness scales with traffic volume
            edge_weight = min(max(trips / 10, 1), 5) 
            
            # Create an interactive tooltip for the edge
            edge_tooltip = (
                f"<b>Route:</b> {data.get('route_type', 'Unknown')}<br>"
                f"<b>Time:</b> {data.get('time_of_day', 'Unknown')}<br>"
                f"<b>Delay Ratio:</b> {delay:.2f}x<br>"
                f"<b>Total Trips:</b> {trips}"
            )
            
            folium.PolyLine(
                locations=[start_coords, end_coords],
                color=delay_cmap(delay),
                weight=edge_weight,
                opacity=0.6,
                tooltip=edge_tooltip
            ).add_to(logistics_map)
            rendered_edges += 1
    print(f"Rendered {rendered_edges} corridors on the map.")

    # 6. Draw the Hubs (Nodes)
    print("Rendering hubs...")
    rendered_nodes = 0
    for node, data in G.nodes(data=True):
        if 'lat' in data and 'lon' in data:
            bc_score = data.get('betweenness', 0)
            
            # Base radius + massive multiplier for high betweenness hubs
            hub_radius = 3 + (bc_score * 500) # Adjust multiplier based on your data spread
            
            # Create a rich HTML popup for the hub
            hub_popup = folium.Popup(
                f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <h4 style="margin-bottom: 5px;">{data.get('name', node)}</h4>
                    <b>ID:</b> {node}<br>
                    <b>Chokehold Score:</b> {bc_score:.6f}<br>
                    <b>In-Degree:</b> {data.get('in_degree', 0)}<br>
                    <b>Out-Degree:</b> {data.get('out_degree', 0)}
                </div>
                """,
                max_width=300
            )
            
            folium.CircleMarker(
                location=[data['lat'], data['lon']],
                radius=hub_radius,
                color=chokehold_cmap(bc_score),
                fill=True,
                fill_color=chokehold_cmap(bc_score),
                fill_opacity=0.8,
                popup=hub_popup,
                tooltip=f"{data.get('name', node)} (Click for metrics)"
            ).add_to(logistics_map)
            rendered_nodes += 1
    print(f"Rendered {rendered_nodes} hubs on the map.")

    # 7. Save the Output
    logistics_map.save(output_file)
    print(f"Map saved! Open {output_file} in your browser.")

if __name__ == "__main__":
    main()