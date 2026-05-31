import os
import sys

# Add parent directory of pipeline to path to support running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.preprocessing import load_data, preprocess_data
from pipeline.aggregation import aggregate_edges
from pipeline.graph import initialize_graph

def main():
    print("==================================================")
    print("  Delhivery Graph Construction Pipeline Runner")
    print("==================================================")
    
    # Paths are resolved relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cleaned_csv_path = os.path.join(current_dir, "..", "cleaning", "cleaned_delivery_data.csv")
    
    try:
        # Step 1: Pre-process
        df_raw = load_data(cleaned_csv_path)
        df_preprocessed = preprocess_data(df_raw)
        
        # Step 2: Aggregate
        aggregated_edges = aggregate_edges(df_preprocessed)
        
        # Step 3: Construct Graph
        G = initialize_graph(df_preprocessed, aggregated_edges)
        
        print("\n==================================================")
        print("  Pipeline Results & Verification")
        print("==================================================")
        print(f"Graph Class: {type(G).__name__}")
        print(f"Facility Nodes count: {G.number_of_nodes()}")
        print(f"Corridor Edges count: {G.number_of_edges()}")
        
        # Verify node properties
        print("\nNode samples:")
        sample_nodes = list(G.nodes)[:3]
        for node_id in sample_nodes:
            print(f"  - Facility ID: {node_id} | Attributes: {G.nodes[node_id]}")
            
        # Verify edge properties
        print("\nEdge samples:")
        sample_edges = list(G.edges(keys=True, data=True))[:3]
        for u, v, key, data in sample_edges:
            print(f"  - Corridor {u} -> {v} (Key: {key}) | Attributes: {data}")
            
        print("\n==================================================")
        print("  Execution Finished Successfully!")
        print("==================================================")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
