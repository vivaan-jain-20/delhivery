# 📊 Delhivery Logistics Network Optimizer & Graph ETA Engine

A modular logistics optimization and machine learning project designed to construct, visualize, and predict transit metrics across Delhivery's national supply chain web. This project builds a directed network graph (`networkx.DiGraph`) from raw trip segments, maps logistics hubs using postal datasets, identifies topological chokeholds, and deploys a state-of-the-art Histogram Gradient Boosting engine augmented with 2-Hop Spatial GraphSAGE features to maximize arrival time predictions, boost SLA compliance targets, and optimize structural fleet deployment (FTL vs. Carting).

---

## 📁 Repository Structure

The project is structured into four self-contained, sequential pipeline directories:

1. **`cleaning/`**: 
   * Preprocesses raw delivery trip datasets (`delivery_data.csv`). 
   * Handles anomalous negative/zero-duration records, filters statistical outliers, parses timestamp objects, maps categorical time-of-day slots, and generates a structured core base dataset.
2. **`graph_building_pipeline/`**: 
   * Constructs the master logistics topology network graph (`delhivery_graph.pkl`).
   * Defines facility node boundaries, registers edge parameters across center-to-center corridors, and maps transit density properties.
3. **`graph_visualizations/`**: 
   * Generates interactive, web-based HTML maps of the logistics networks.
   * Includes structural physics layouts (PyVis with gravity simulations) and geographic heatmaps (Folium map nodes sized by bottleneck centrality and routes colored by real-world transit delays).
   * Houses the strategic **Graph Analysis & Strategy Guide**.
4. **`Graph-enhanced ETA prediction model/`**:
   * Architectures the machine learning optimization, benchmarking, and decision-routing frameworks.
   * Implements a localized 2-Hop Spatial Neighborhood Aggregator (inspired by GraphSAGE) and matrix PageRank power-iterations to convert complex network shapes into 16-dimensional edge feature vectors.
   * Compares a traditional tabular model against a high-speed histogram boosting ensemble (`HistGradientBoostingRegressor`) optimized directly under absolute error criteria.
   * Deploys a **Digital Twin counterfactual scenario simulator** (`route_optimization_framework.py`) that models parallel routing types (FTL vs. Carting) to calculate exact speed-cost trade-offs relative to a corridor's distance, time-of-day, and origin hub infrastructure risk.

---

## 🚀 Getting Started (How to Run)

Follow these steps to set up, initialize, and execute the entire network optimization, machine learning, and fleet routing pipeline:

### 1. Place the Dataset
* Obtain your raw dataset `delivery_data.csv` (approx. 55MB) and place it directly in the **root directory** of this repository.

### 2. Environment Setup
Create and activate an isolated Python virtual environment, then install all project requirements:

```bash
# 1. Create a local virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Cmd):
.\venv\Scripts\activate.bat

# 3. Install required packages
python3 -m pip install -r requirements.txt

# Step A: Clean and preprocess the raw data
python3 cleaning/clean.py

# Step B: Build the NetworkX topology graph layout
python3 graph_building_pipeline/run_pipeline.py

# Step C: Generate interactive structural and geographical HTML maps
python3 graph_visualizations/visualize.py
python3 graph_visualizations/visualize_geo.py

# Step D: Extract 2-Hop spatial embeddings and build ML feature matrices
python3 "Graph-enhanced ETA prediction model/prepare_ml_data.py"

# Step E: Train and benchmark high-speed gradient boosting regression models
python3 "Graph-enhanced ETA prediction model/train_models.py"

# Step F: Run counterfactual simulations to optimize fleet routing (FTL vs. Carting)
python3 "Graph-enhanced ETA prediction model/route_optimization_framework.py"