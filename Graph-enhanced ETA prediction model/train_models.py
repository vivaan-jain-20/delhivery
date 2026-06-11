import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import warnings

warnings.filterwarnings('ignore')

def run_ml_benchmark():
    print("[1/3] Loading pre-processed ML data matrices...")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_ml = os.path.join(base_dir, 'ml_data')
        repo_ml = os.path.abspath(os.path.join(base_dir, '..', 'ml_data'))

        # Route to the correct matrix data directory
        if os.path.exists(os.path.join(script_ml, 'X_train_baseline.npy')):
            data_dir = script_ml
        elif os.path.exists(os.path.join(repo_ml, 'X_train_baseline.npy')):
            data_dir = repo_ml
        else:
            raise FileNotFoundError('ml_data not found next to script or in repo root')

        X_tr_b = np.load(os.path.join(data_dir, 'X_train_baseline.npy'), allow_pickle=True)
        X_te_b = np.load(os.path.join(data_dir, 'X_test_baseline.npy'), allow_pickle=True)
        X_tr_g = np.load(os.path.join(data_dir, 'X_train_graph.npy'), allow_pickle=True)
        X_te_g = np.load(os.path.join(data_dir, 'X_test_graph.npy'), allow_pickle=True)
        y_tr = np.load(os.path.join(data_dir, 'y_train.npy'), allow_pickle=True)
        y_te = np.load(os.path.join(data_dir, 'y_test.npy'), allow_pickle=True)
    except FileNotFoundError:
        print("[ERROR] Data not found! Please run 'python prepare_ml_data.py' first.")
        return

    # PREMIUM GRADIENT BOOSTING CONFIGURATION
    # loss='absolute_error' optimizes for MAE natively using fast histogram binning
    model_config = {
        'loss': 'absolute_error',
        'max_iter': 100,          # Number of sequential boosting trees built
        'max_depth': 12,          # Protects against deep overfitting
        'learning_rate': 0.1,     # Shrinkage factor to ensure stable convergence
        'random_state': 42,
        'verbose': 0              # Kept quiet because execution completes almost instantly
    }
    
    print(f"[2/3] Training  Tabular Boosting Model on all {len(X_tr_b):,} rows...")
    gbt_base = HistGradientBoostingRegressor(**model_config)
    gbt_base.fit(X_tr_b, y_tr)
    preds_base = gbt_base.predict(X_te_b)
    
    print(f"[3/3] Training  Graph-Enhanced Boosting Model on all {len(X_tr_g):,} rows...")
    gbt_graph = HistGradientBoostingRegressor(**model_config)
    gbt_graph.fit(X_tr_g, y_tr)
    preds_graph = gbt_graph.predict(X_te_g)

    # Save the trained models using pickle
    print(f"Saving trained models to: {data_dir}")
    import pickle
    with open(os.path.join(data_dir, 'gbt_base.pkl'), 'wb') as f:
        pickle.dump(gbt_base, f)
    with open(os.path.join(data_dir, 'gbt_graph.pkl'), 'wb') as f:
        pickle.dump(gbt_graph, f)
    
    # Mathematical performance verification
    mae_b = mean_absolute_error(y_te, preds_base)
    mae_g = mean_absolute_error(y_te, preds_graph)
    p15_b = np.mean(np.abs(preds_base - y_te) / y_te <= 0.15) * 100
    p15_g = np.mean(np.abs(preds_graph - y_te) / y_te <= 0.15) * 100
    
    print("\n==================================================")
    print("  GRAPH ADVANTAGE SCOREBOARD")
    print("==================================================")
    print(f"BASELINE BOOSTING MODEL (Traditional Tabular Features)")
    print(f"  - MAE: {mae_b:.4f} mins | SLA Target: {p15_b:.2f}%")
    print(f"GRAPH-ENHANCED BOOSTING MODEL (With Deep GraphSAGE)")
    print(f"  - MAE: {mae_g:.4f} mins | SLA Target: {p15_g:.2f}%")
    print("-" * 50)
    print(f"NET GRAPH ADVANTAGE (MAE Lift): {mae_b - mae_g:.4f} mins")
    print(f"NET GRAPH ADVANTAGE (SLA Lift): +{p15_g - p15_b:.2f}%")
    print("==================================================\n")

if __name__ == "__main__":
    run_ml_benchmark()