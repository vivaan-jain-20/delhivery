import networkx as nx
import pandas as pd
from models import FacilityNode, CorridorEdge

def initialize_graph(df: pd.DataFrame, aggregated_edges: pd.DataFrame) -> nx.MultiDiGraph:
    """
    Constructs a networkx.MultiDiGraph() from the preprocessed DataFrame and aggregated edges:
    - Extracts the unique union of both source and destination centers to instantiate FacilityNode dataclasses.
    - Adds nodes to G using G.add_node(node.id, **node.__dict__).
    - Instantiates CorridorEdge dataclasses from the aggregated edges.
    - Adds edges to G using G.add_edge(edge.source, edge.destination, **edge.__dict__).
    - Updates in_degree and out_degree attributes of nodes based on the final graph topology.
    """
    print("Initializing MultiDiGraph...")
    G = nx.MultiDiGraph()

    # 1. Extract unique union of BOTH source and destination centers
    print("Extracting unique union of facility nodes...")
    source_nodes = df[['source_center', 'source_name']].rename(
        columns={'source_center': 'id', 'source_name': 'name'}
    )
    dest_nodes = df[['destination_center', 'destination_name']].rename(
        columns={'destination_center': 'id', 'destination_name': 'name'}
    )
    
    # Concatenate and drop duplicates by ID to get a unique set of all physical centers
    all_nodes_df = pd.concat([source_nodes, dest_nodes]).dropna(subset=['id']).drop_duplicates(subset=['id'])
    print(f"Total unique facility nodes found: {len(all_nodes_df)}")

    # Add nodes to the graph
    for _, row in all_nodes_df.iterrows():
        node = FacilityNode(id=str(row['id']), name=str(row['name']))
        G.add_node(node.id, **node.__dict__)

    # 2. Add aggregated edges to the graph
    print("Adding corridors (edges) to the graph...")
    for _, row in aggregated_edges.iterrows():
        edge = CorridorEdge(
            source=str(row['source_center']),
            destination=str(row['destination_center']),
            route_type=str(row['route_type']),
            time_of_day=str(row['time_of_day']),
            median_delay_ratio=float(row['median_delay_ratio']),
            total_trips=int(row['total_trips'])
        )
        # MultiDiGraph natively supports multiple parallel edges
        G.add_edge(edge.source, edge.destination, **edge.__dict__)

    # 3. Post-processing: update degrees on each node attribute dict
    print("Updating node in_degree and out_degree properties...")
    for node_id in G.nodes:
        G.nodes[node_id]['in_degree'] = G.in_degree(node_id)
        G.nodes[node_id]['out_degree'] = G.out_degree(node_id)

    print(f"Graph initialization complete. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    return G
