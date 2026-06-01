# 📊 Delhivery Logistics Network Optimizer

A modular logistics optimization project designed to construct and visualize Delhivery's national transit web. This project builds a directed network graph (`networkx.MultiDiGraph`) from raw trip segments, maps logistics centers to geographical coordinates using postal data, identifies bottleneck hubs using betweenness centrality, and generates interactive visualizations (HTML maps) for analysis.

---

## 📁 Repository Structure

The project is structured into three self-contained folders:

1. **[`cleaning/`](file:///c:/Users/Vivaa/OneDrive/Desktop/vsc/delhivery/cleaning/README.md)**: 
   * Preprocesses raw delivery trip datasets. 
   * Cleans anomalous negative/zero-duration records, filters outliers, parses timestamp structures, maps categorical times of day, and drops internal tracking data.
2. **[`graph_building_pipeline/`](file:///c:/Users/Vivaa/OneDrive/Desktop/vsc/delhivery/graph_building_pipeline/README.md)**: 
   * Constructs the logistics transit graph.
   * Definess dataclass models, maps facility nodes (using the union of source and destination centers), groups parallel edge paths, and calculates network node degrees.
3. **[`graph_visualizations/`](file:///c:/Users/Vivaa/OneDrive/Desktop/vsc/delhivery/graph_visualizations/README.md)**: 
   * Generates interactive, web-based visual maps of the logistics networks.
   * Includes structural network maps (PyVis layout with gravity controls) and geographical heatmaps (Folium map colored by transit delay and sized by chokehold criticality).
   * Includes the **[Graph Analysis & Strategy Guide](file:///c:/Users/Vivaa/OneDrive/Desktop/vsc/delhivery/graph_visualizations/graph_analysis_guide.md)**.

---

## 🚀 Getting Started (How to Run)

Follow these steps to set up and run the pipeline:

### 1. Place the Dataset
* Obtain the raw dataset `delivery_data.csv` (approx. 55MB) and place it directly in the root folder of this project.

### 2. Environment Setup
Create and activate an isolated Python virtual environment, and install the required dependencies:

```bash
# 1. Create a local virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Cmd):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# 3. Install packages
pip install -r requirements.txt
```

### 3. Run the Code

Execute the pipeline in sequential order:

```bash
# Step A: Clean and preprocess the raw data
python cleaning/clean.py

# Step B: Build the NetworkX graph
python graph_building_pipeline/run_pipeline.py

# Step C: Generate interactive visualizations
python graph_visualizations/visualize.py
python graph_visualizations/visualize_geo.py
```

Outputs will be saved in their respective directories (visualizations are saved as HTML maps inside `graph_visualizations/`).
