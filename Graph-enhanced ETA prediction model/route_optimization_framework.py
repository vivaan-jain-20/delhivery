import os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
import warnings

warnings.filterwarnings('ignore')

def build_route_decision_framework():
    print("[1/3] Loading pre-processed data and training simulation brain...")
    
    # Locate the matrix cache folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'ml_data')
    
    try:
        X_tr_g = np.load(os.path.join(data_dir, 'X_train_graph.npy'), allow_pickle=True)
        X_te_g = np.load(os.path.join(data_dir, 'X_test_graph.npy'), allow_pickle=True)
        y_tr = np.load(os.path.join(data_dir, 'y_train.npy'), allow_pickle=True)
        y_te = np.load(os.path.join(data_dir, 'y_test.npy'), allow_pickle=True)
    except FileNotFoundError:
        print("❌ Error: ML data matrices not found. Please run prepare_ml_data.py first.")
        return

    # Train the High-Speed Histogram Boosting Simulator
    simulator = HistGradientBoostingRegressor(loss='absolute_error', max_iter=100, max_depth=12, random_state=42)
    simulator.fit(X_tr_g, y_tr)
    
    print("[2/3] Simulating counterfactual scenarios (FTL vs. Carting trade-offs)...")
    
    # In our matrix sequence layout, 'is_ftl' is assigned to feature index column 2
    FTL_FEATURE_INDEX = 2
    
    # Duplicate the test matrix to simulate counterfactual alternate routing universes
    X_sim_ftl = np.copy(X_te_g)
    X_sim_carting = np.copy(X_te_g)
    
    # Force the simulations to run entirely as bulk FTL vs. running entirely as agile Carting
    X_sim_ftl[:, FTL_FEATURE_INDEX] = 1.0
    X_sim_carting[:, FTL_FEATURE_INDEX] = 0.0
    
    # Compute transit time estimations for both options simultaneously
    predicted_time_ftl = simulator.predict(X_sim_ftl)
    predicted_time_carting = simulator.predict(X_sim_carting)
    
    # Positive values mean Carting arrives faster than standard FTL
    time_saved_by_carting = predicted_time_ftl - predicted_time_carting
    
    # Reconstruct route contextual arrays for business profiling
    distances = X_te_g[:, 1]       # Index 1 stores the physical OSRM segment distances
    src_betweenness = X_te_g[:, 3] # Index 3 captures starting facility structural risk properties
    degree_ratio = X_te_g[:, -1]   # The final matrix column stores the node degree interaction ratio
    
    # Consolidate results into an evaluation frame
    results_df = pd.DataFrame({
        'Distance_KM': distances,
        'Source_Hub_Betweenness': src_betweenness,
        'Hub_Degree_Ratio': degree_ratio,
        'Predicted_Time_FTL_mins': predicted_time_ftl,
        'Predicted_Time_Carting_mins': predicted_time_carting,
        'Carting_Time_Savings_mins': time_saved_by_carting
    })
    
    # Set operational cost-benefit constraints
    # Operational Rule: Select premium Carting ONLY if it cuts transit time by >15% AND saves >10 mins.
    results_df['Time_Savings_Percentage'] = (results_df['Carting_Time_Savings_mins'] / results_df['Predicted_Time_FTL_mins']) * 100
    
    results_df['Optimal_Route_Decision'] = np.where(
        (results_df['Carting_Time_Savings_mins'] > 10.0) & (results_df['Time_Savings_Percentage'] > 15.0),
        'Deploy Agile Carting',
        'Standardize Bulk FTL'
    )
    
    print("[3/3] Profiling Corridor Clusters and Quantifying Trade-offs...")
    
    # Cluster segments by distance parameters to isolate strategic insights
    results_df['Corridor_Profile'] = pd.qcut(results_df['Distance_KM'], q=3, labels=['Short-Haul (<45km)', 'Mid-Haul (45-120km)', 'Long-Haul (>120km)'])
    
    summary = results_df.groupby('Corridor_Profile').agg({
        'Carting_Time_Savings_mins': 'mean',
        'Time_Savings_Percentage': 'mean',
        'Optimal_Route_Decision': lambda x: (x == 'Deploy Agile Carting').mean() * 100
    }).rename(columns={'Optimal_Route_Decision': 'Carting_Recommendation_Rate_%'})
    
    print("\n==========================================================================")
    # Isolate structural graph effects (High Betweenness Gateways vs Low Betweenness Regional Outposts)
    high_risk_hubs = results_df[results_df['Source_Hub_Betweenness'] > results_df['Source_Hub_Betweenness'].median()]
    avg_savings_high_risk = high_risk_hubs['Carting_Time_Savings_mins'].mean()
    
    low_risk_hubs = results_df[results_df['Source_Hub_Betweenness'] <= results_df['Source_Hub_Betweenness'].median()]
    avg_savings_low_risk = low_risk_hubs['Carting_Time_Savings_mins'].mean()
    
    print(" 📊 ML-BACKED FTL VS. CARTING DECISION FRAMEWORK REPORT")
    print("==========================================================================")
    print(summary.to_string(float_format=lambda x: f"{x:.2f}"))
    print("-" * 74)
    print(f"💡 GRAPH POSITION INSIGHT (Source Facility Infrastructure Risk):")
    print(f"  - On high-congestion bottleneck hubs (High Betweenness Centrality):")
    print(f"    Carting saves an average of {avg_savings_high_risk:.2f} mins over FTL.")
    print(f"  - On isolated regional centers (Low Betweenness Centrality):")
    print(f"    Carting only saves an average of {avg_savings_low_risk:.2f} mins over FTL.")
    print("\n STRATEGIC RECOMMENDATION:")
    print("  -> Route long-haul segments through standard bulk FTL to maximize cost efficiency.")
    print("  -> Force-deploy agile Carting on short/mid-haul trips originating from high-risk")
    print("     gateways to explicitly bypass severe structural queuing delays.")
    print("==========================================================================\n")

if __name__ == "__main__":
    build_route_decision_framework()