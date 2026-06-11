# Graph Visualizations Component

This directory contains scripts that translate our serialized logistics network graph into interactive, web-based HTML visualizations.

## File Overview

* **`visualize.py`**: Generates `delhivery_network.html` using PyVis.
  * *Features*: Physics layout panel, zoom, drag, and gravity controls. Nodes are color-coded in light green, and edges are colored red (if delay ratio $> 1.2$) or blue (if delay ratio $\le 1.2$).
* **`visualize_geo.py`**: Generates `delhivery_geo_network.html` using Folium and Branca.
  * *Features*: Real geographical overlay across India using leaflet and cartodb dark matter tile theme. Node size/color maps to betweenness centrality (chokehold risk). Edge thickness/color maps to trip volume and OSRM delay ratios.
* **`graph_analysis_guide.md`**: A detailed guide describing the visual attributes and features (nodes, edges, thicknesses, colors, popups) and how they translate to strategic memo writing.

---

## Generated HTML Visualizations (Outputs)

Running the scripts generates two standalone HTML map files inside this folder:
* **`delhivery_network.html`** *(ignored by git)*: Interactive physics network.
* **`delhivery_geo_network.html`** *(ignored by git)*: Interactive geographical leaflet map.
* **`pincodes_coordinates.csv`** *(ignored by git)*: Cached coordinate dictionary mapping PIN codes to latitude and longitude.

---

## How to Run

Before running, ensure `graph_building_pipeline/run_pipeline.py` has completed and generated `graph_building_pipeline/delhivery_graph.pkl`.

Execute the scripts using the virtual environment:

```bash
# Generate the PyVis physics network map
python graph_visualizations/visualize.py

# Generate the Folium geographical transit map
python graph_visualizations/visualize_geo.py
```

Open the resulting `.html` files in any web browser to explore the networks.
