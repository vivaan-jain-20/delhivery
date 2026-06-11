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
5. **Streamlit Control Tower Dashboard (`app.py`, `pages/`)**:
   * A premium, multi-page frontend dashboard built for a Network Operations Leader.
   * Integrates live with backend NetworkX topologies and HistGradientBoosting ML models.
   * Key pages:
     * **Landing Page (`app.py`)**: Renders high-level KPIs and integrates the interactive Folium geospatial map.
     * **Bottleneck Audit (`pages/1_Bottleneck_Audit.py`)**: Computes and ranks nodes by PageRank and Betweenness Centrality on the fly, with an investment payoff simulator.
     * **ETA Prediction (`pages/2_ETA_Prediction.py`)**: Runs live model predictions comparing OSRM baselines and GraphSAGE predictions for selected routes.
     * **Route Optimization (`pages/3_Route_Optimization.py`)**: Executes counterfactual FTL vs. Carting simulations and applies operational hurdle rules.

---

## 🚀 Getting Started (How to Run)

Follow these steps to set up, initialize, and execute the entire network optimization, machine learning, and fleet routing pipeline:

### 1. Place the Dataset
* Obtain your raw dataset `delivery_data.csv` (approx. 55MB) and place it directly in the **root directory** of this repository.

### 2. Environment Setup & Execution
Follow these modular commands to initialize and run the pipeline step by step:

**Create the local virtual environment:**
```bash
python -m venv venv
```

**Activate the virtual environment:**
* For **macOS / Linux / POSIX (MSYS2/Git Bash)**:
```bash
source venv/bin/activate
```
* For **Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```
* For **Windows (Command Prompt)**:
```cmd
.\venv\Scripts\activate.bat
```

**Install required packages:**
```bash
python -m pip install -r requirements.txt
```

---

### 3. Pipeline Execution Steps

Execute the data, visualization, and machine learning pipeline sequentially:

**Step A: Clean and preprocess the raw delivery data**
```bash
python cleaning/clean.py
```

**Step B: Build the NetworkX topology graph layout**
```bash
python graph_building_pipeline/run_pipeline.py
```

**Step C: Generate interactive structural and geographical HTML maps**
```bash
python graph_visualizations/visualize.py
python graph_visualizations/visualize_geo.py
```

**Step D: Extract 2-Hop spatial embeddings and build ML feature matrices**
```bash
python "Graph-enhanced ETA prediction model/prepare_ml_data.py"
```

**Step E: Train and benchmark high-speed gradient boosting regression models**
```bash
python "Graph-enhanced ETA prediction model/train_models.py"
```

**Step F: Run counterfactual simulations to optimize fleet routing (FTL vs. Carting)**
```bash
python "Graph-enhanced ETA prediction model/route_optimization_framework.py"
```

**Step G: Launch the Control Tower Streamlit Dashboard**
```bash
streamlit run app.py
```

---

## 💻 Cross-Platform Compatibility

To ensure this project runs seamlessly across Windows, macOS, Linux, and POSIX terminal environments (such as MSYS2 or Git Bash):

1. **Virtual Environment Interpreter Resolution (`python` vs. `python3`):**
   * On Windows, virtual environments only contain `python.exe` and do **not** create a `python3.exe` alias.
   * If you use `python3` after activating a virtual environment on Windows, the shell will bypass the virtual environment and fallback to your global python interpreter (e.g. MSYS2's compiler environment).
   * **Best Practice:** Once the virtual environment is activated, always use the command **`python`** instead of `python3`. This ensures dependencies are read from and installed to the local virtual environment.
2. **File Path Separators:**
   * Source scripts use Python's standard `pathlib` and `os.path` libraries rather than hardcoded slashes. Path separators automatically adapt to the host operating system's native formats.
3. **Ignore Binaries & Caches:**
   * Keep compiled files, local environment directories (`venv/`), `.pkl` models, and `.npy` arrays out of Git versioning. They are fully pre-configured in `.gitignore`.