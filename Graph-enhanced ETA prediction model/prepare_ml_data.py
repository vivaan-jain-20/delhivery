import os
import pickle
import pandas as pd
import numpy as np
import networkx as nx
import warnings

warnings.filterwarnings('ignore')

def load_assets():
    """
    Loads pipeline assets matching your exact folder architecture layout:
    - cleaned_delivery_data.csv from /cleaning
    - delhivery_graph.pkl from /graph_building_pipeline
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Support two layouts:
    # 1) script sits at repository root (original layout)
    # 2) script sits inside the "Graph-enhanced ETA prediction model" folder
    # We try the script directory first, then fallback to one level up.
    repo_root = os.path.abspath(os.path.join(current_dir, ".."))

    # Route to the cleaning folder for the dataset (try both locations)
    cleaning_dir_candidates = [
        os.path.join(current_dir, "cleaning"),
        os.path.join(repo_root, "cleaning")
    ]

    pipeline_dir_candidates = [
        os.path.join(current_dir, "graph_building_pipeline"),
        os.path.join(repo_root, "graph_building_pipeline")
    ]

    csv_path = None
    for c in cleaning_dir_candidates:
        candidate = os.path.join(c, "cleaned_delivery_data.csv")
        if os.path.exists(candidate):
            csv_path = candidate
            cleaning_dir = c
            break

    graph_path = None
    for p in pipeline_dir_candidates:
        candidate = os.path.join(p, "delhivery_graph.pkl")
        if os.path.exists(candidate):
            graph_path = candidate
            pipeline_dir = p
            break
    
    print("[1/4] Fetching pipeline assets matching folder layout...")
    
    # Friendly defensive checks to make debugging easy
    if csv_path is None:
        raise FileNotFoundError(
            f"\n❌ Missing dataset. Tried locations:\n  - {cleaning_dir_candidates[0]}/cleaned_delivery_data.csv\n  - {cleaning_dir_candidates[1]}/cleaned_delivery_data.csv\n"
            f"Please make sure your data cleaning script has run and saved the file in one of these locations."
        )
    if graph_path is None:
        raise FileNotFoundError(
            f"\n❌ Missing network graph. Tried locations:\n  - {pipeline_dir_candidates[0]}/delhivery_graph.pkl\n  - {pipeline_dir_candidates[1]}/delhivery_graph.pkl\n"
            f"Please make sure your graph generation pipeline has run and saved the pickle file in one of these locations."
        )
        
    df = pd.read_csv(csv_path)
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
        
    # Standardize to DiGraph for consistent feature aggregation
    if isinstance(G, nx.MultiDiGraph):
        G = nx.DiGraph(G)
        
    return df, G

def extract_deep_graphsage_features(G: nx.DiGraph) -> dict:
    """
    Implements a 2-Hop spatial neighborhood message aggregator 
    inspired by GraphSAGE architecture to capture network structural traits.
    """
    print("[2/4] Engineering Deep GraphSAGE Spatial Graph Features...")
    
    # Calculate fundamental structural metrics
    betweenness = nx.betweenness_centrality(G)
    clustering = nx.clustering(G)
    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())
    
    # --- 1-Hop Neighborhood Aggregation ---
    graphsage_1hop = {}
    for node in G.nodes():
        self_features = np.array([
            betweenness.get(node, 0.0), clustering.get(node, 0.0),
            in_degree.get(node, 0.0), out_degree.get(node, 0.0)
        ])
        successors = list(G.successors(node))
        if len(successors) > 0:
            neigh_matrix = [[betweenness.get(s, 0.0), clustering.get(s, 0.0), in_degree.get(s, 0.0), out_degree.get(s, 0.0)] for s in successors]
            agg_1hop = np.mean(neigh_matrix, axis=0)
        else:
            agg_1hop = np.zeros(4)
        graphsage_1hop[node] = np.concatenate([self_features, agg_1hop])

    # --- 2-Hop Neighborhood Aggregation ---
    graphsage_2hop = {}
    for node in G.nodes():
        current_1hop = graphsage_1hop[node]
        successors = list(G.successors(node))
        if len(successors) > 0:
            neigh_2hop_matrix = [graphsage_1hop.get(s, np.zeros(8)) for s in successors]
            agg_2hop = np.mean(neigh_2hop_matrix, axis=0)
        else:
            agg_2hop = np.zeros(8)
        graphsage_2hop[node] = np.concatenate([current_1hop, agg_2hop])
        
    return graphsage_2hop

def assemble_matrices(df: pd.DataFrame, embeddings: dict):
    """
    Flattens spatial nodes into edge feature vectors and injects 
    topological relationship interaction metrics to build downstream matrices.
    """
    print("[3/4] Assembling ML Matrices with Topological Interaction Deltas...")
    
    df = df.copy()
    
    # Encode non-numerical baseline metrics cleanly
    df['is_ftl'] = (df['route_type'] == 'FTL').astype(int)
    if 'time_of_day' in df.columns:
        df = pd.get_dummies(df, columns=['time_of_day'], drop_first=True)
    
    time_cols = [c for c in df.columns if 'time_of_day_' in c]
    baseline_features = ['segment_osrm_time', 'segment_osrm_distance', 'is_ftl'] + time_cols
    
    # Map graph vectors to dataset corridors
    src_vectors, dst_vectors = [], []
    blank_emb = np.zeros(16)  # Safeguard fallback vector for cold-start edge checks
    
    for _, row in df.iterrows():
        src_vectors.append(embeddings.get(str(row['source_center']), blank_emb))
        dst_vectors.append(embeddings.get(str(row['destination_center']), blank_emb))
        
    src_df = pd.DataFrame(src_vectors)
    dst_df = pd.DataFrame(dst_vectors)
    
    # Engineer interaction dynamics between source and destination facilities
    interaction_df = pd.DataFrame()
    interaction_df['betweenness_delta'] = dst_df[0] - src_df[0]
    interaction_df['clustering_delta'] = dst_df[1] - src_df[1]
    interaction_df['degree_ratio'] = (dst_df[2] + 1) / (src_df[3] + 1)

    # Split into evaluation benchmarks
    X_baseline = df[baseline_features].values
    X_graph = np.hstack([X_baseline, src_df.values, dst_df.values, interaction_df.values])
    y = df['segment_actual_time'].values

    # Adhere to custom dataframe split if present, fallback to standard random split
    if 'data' in df.columns:
        is_train = df['data'] == 'training'
    else:
        np.random.seed(42)
        is_train = np.random.rand(len(df)) < 0.8
    
    return X_baseline[is_train], X_baseline[~is_train], X_graph[is_train], X_graph[~is_train], y[is_train], y[~is_train]

if __name__ == "__main__":
    try:
        df, G = load_assets()
        sage_embeddings = extract_deep_graphsage_features(G)
        X_tr_b, X_te_b, X_tr_g, X_te_g, y_tr, y_te = assemble_matrices(df, sage_embeddings)

        print("[4/4] Serializing Matrix Partitions directly to disk storage...")
        # Persist ml_data next to this script to avoid surprises from different cwd's
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(script_dir, 'ml_data')
        os.makedirs(out_dir, exist_ok=True)

        # Save sage_embeddings dictionary to pickle format
        embeddings_path = os.path.join(out_dir, 'sage_embeddings.pkl')
        print(f"Saving sage embeddings to: {embeddings_path}")
        with open(embeddings_path, 'wb') as f:
            pickle.dump(sage_embeddings, f)

        # FIX: Force everything to float64 numbers before saving to prevent Object arrays
        np.save(os.path.join(out_dir, 'X_train_baseline.npy'), X_tr_b.astype(np.float64))
        np.save(os.path.join(out_dir, 'X_test_baseline.npy'), X_te_b.astype(np.float64))
        np.save(os.path.join(out_dir, 'X_train_graph.npy'), X_tr_g.astype(np.float64))
        np.save(os.path.join(out_dir, 'X_test_graph.npy'), X_te_g.astype(np.float64))
        np.save(os.path.join(out_dir, 'y_train.npy'), y_tr.astype(np.float64))
        np.save(os.path.join(out_dir, 'y_test.npy'), y_te.astype(np.float64))

        print("\n=======================================================")
        print(" [SUCCESS] ML DATA PIPELINE EXECUTED SUCCESSFULLY!")
        print(f" Data matrices generated and saved in '{out_dir}'")
        print(" Run 'python train_models.py' to observe graph performance.")
        print("=======================================================\n")

    except Exception as e:
        print(f"\n[ERROR] Execution Failed: {e}")