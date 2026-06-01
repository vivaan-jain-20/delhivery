# 🕸️ Graph Building Pipeline Component

This directory contains the Python modules to reconstruct the logistics transit corridors from segment data and build the `networkx.MultiDiGraph` network structure.

## 📄 File Overview

* **`models.py`**: Defines the `FacilityNode` (nodes) and `CorridorEdge` (edges) memory-efficient Python dataclasses.
* **`preprocessing.py`**: Removes zero-duration estimates (`segment_osrm_time <= 0`) and calculates the `delay_ratio = segment_actual_time / segment_osrm_time`.
* **`aggregation.py`**: Group and aggregate raw edge traversals by origin, destination, route type, and time of day. Calculates the median delay ratio and total trip count, filtering out any corridors with $< 5$ trips to reduce noise.
* **`graph.py`**: Extracts the unique union of both source and destination centers, initializes node/edge dataclasses, populates the `networkx.MultiDiGraph`, and updates structural degree metrics on the node attributes.
* **`run_pipeline.py`**: Orchestrates the entire pipeline process end-to-end, printing data shapes and saving the serialized graph structure.
* **`delhivery_graph.pkl`** *(ignored by git)*: The serialized representation of the constructed `networkx.MultiDiGraph` used by the downstream visualization scripts.

---

## ⚙️ Pipeline Steps

1. **Pre-processing**: Loads `cleaning/cleaned_delivery_data.csv` and filters out any rows where `segment_osrm_time <= 0` (division-by-zero safeguard). Calculates the delay ratio.
2. **Aggregation**: Groups records by `(source_center, destination_center, route_type, time_of_day)`. Finds the median delay ratio and count of trips. Filters out groups with $< 5$ trips.
3. **Graph Initialization**: Instantiates `FacilityNode` for all unique centers (union of both source and destination columns) and adds them to `nx.MultiDiGraph()`. Adds `CorridorEdge` edges (natively supporting parallel routes like FTL vs Carting or Night vs Morning between the same cities). Finally, computes and stores each node's `in_degree` and `out_degree`.
4. **Serialization**: Saves the fully constructed graph as a binary pickle file: `delhivery_graph.pkl`.

---

## 🚀 How to Run

Run the orchestrator script using the virtual environment:

```bash
python graph_building_pipeline/run_pipeline.py
```
