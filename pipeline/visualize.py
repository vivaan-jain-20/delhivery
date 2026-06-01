import os
import sys
import pickle
from pyvis.network import Network

# Ensure the parent directory is in the path to run directly if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visualization():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    graph_pkl_path = os.path.join(current_dir, "delhivery_graph.pkl")
    output_html_path = os.path.join(current_dir, "..", "delhivery_network.html")

    print(f"Loading NetworkX graph from: {graph_pkl_path}...")
    if not os.path.exists(graph_pkl_path):
        raise FileNotFoundError(
            f"Pickled graph not found at {graph_pkl_path}. Please run run_pipeline.py first to build the graph."
        )

    with open(graph_pkl_path, 'rb') as f:
        G = pickle.load(f)

    print(f"Graph loaded successfully. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    # Initialize PyVis network
    print("Initializing PyVis network map...")
    net = Network(
        height="800px", 
        width="100%", 
        directed=True, 
        bgcolor="#222222", 
        font_color="white"
    )

    # 1. Add nodes manually to configure labels and tooltips (titles)
    print("Populating nodes in PyVis...")
    for node_id, data in G.nodes(data=True):
        name = data.get('name', node_id)
        in_degree = data.get('in_degree', 0)
        
        # Tooltip with HTML support
        title = f"Name: {name}<br>In-Degree: {in_degree}"
        
        net.add_node(
            node_id, 
            label=name, 
            title=title, 
            color="#4ade80",  # A nice premium light green color for facility nodes
            size=15 + in_degree * 0.5  # Size nodes dynamically based on in-degree
        )

    # 2. Add edges manually with custom colors and tooltips
    print("Populating edges in PyVis...")
    for u, v, data in G.edges(data=True):
        route_type = data.get('route_type', 'Unknown')
        time_of_day = data.get('time_of_day', 'Unknown')
        median_delay_ratio = data.get('median_delay_ratio', 1.0)
        
        # Color coding: red if median_delay_ratio > 1.2, otherwise blue
        # Using premium shades of red (#ef4444) and blue (#3b82f6) for styling
        color = "#ef4444" if median_delay_ratio > 1.2 else "#3b82f6"
        
        # Tooltip details
        title = (
            f"Route: {route_type}<br>"
            f"Time of Day: {time_of_day}<br>"
            f"Median Delay Ratio: {median_delay_ratio:.3f}"
        )
        
        net.add_edge(
            u, 
            v, 
            title=title, 
            color=color, 
            arrowStrikethrough=False
        )

    # Enable gravity/physics control buttons in browser
    net.show_buttons(filter_=['physics'])

    # Save visualization to an HTML file
    print(f"Generating interactive map and saving to: {os.path.abspath(output_html_path)}...")
    net.show(output_html_path, notebook=False)
    print("Interactive logistics map created successfully!")

if __name__ == "__main__":
    generate_visualization()
