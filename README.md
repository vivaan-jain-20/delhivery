## 📊 Dataset Dictionary

The dataset is structured around **trip segments** (individual hops between logistics hubs) rather than end-to-end journeys. Understanding these segments is critical for accurately modeling the network.

### Identifiers & Categorization
| Feature | Description | Network Role |
| :--- | :--- | :--- |
| `trip_uuid` | Unique identifier for a complete multi-leg journey. Contains an embedded Unix timestamp of creation. | Used to group individual segments into a full route path. |
| `route_schedule_uuid` | System-generated identifier for a specific planned route schedule. | Identifies recurring static paths. |
| `route_type` | The vehicle classification (`FTL` or `Carting`). | Critical for segmenting edge weights and training the route-decision model. |

### Graph Components (Nodes)
| Feature | Description | Network Role |
| :--- | :--- | :--- |
| `source_center` | Unique ID of the starting facility for a specific hop. | **Node (Origin)** |
| `source_name` | Human-readable name of the starting facility. | Node Label / Dashboarding |
| `destination_center` | Unique ID of the ending facility for a specific hop. | **Node (Destination)** |
| `destination_name` | Human-readable name of the ending facility. | Node Label / Dashboarding |

### Target Variables & Edge Weights
| Feature | Description | Network Role |
| :--- | :--- | :--- |
| `actual_time` | Total real-world time taken for the *entire* trip (minutes). | Ground truth for the final ETA prediction model. |
| `osrm_time` | OSRM shortest-path ETA for the *entire* trip (minutes). | Baseline prediction metric. |
| `segment_actual_time` | Real-world time for *just this specific hop* between two hubs. | Used to compute corridor delay ratios. |
| `segment_osrm_time` | OSRM estimated time for *just this specific hop*. | Used to compute corridor delay ratios. |
| `trip_creation_time` | Exact timestamp when the trip was generated. | Used to capture time-of-day features (peak vs. off-peak). |

---

## 🕸️ Graph Construction Strategy

To move from tabular segment data to a `NetworkX` directed graph, we execute a sequential data pipeline. The core philosophy is that **rows in the dataset represent edge traversals (trucks), not the edges themselves (corridors).**

### 1. Data Preprocessing & Journey Reconstruction
Because a single package journey spans multiple rows, we must first reconstruct the full path.
* Group the raw data by `trip_uuid`.
* Sort the grouped data chronologically using the trip creation or start times.
* This exposes the sequence of intermediate hubs visited, ensuring we accurately capture the physical flow of the network.

### 2. Node Definition
* **Nodes** represent the physical Delhivery logistics facilities.
* We extract the unique union of all `source_center` and `destination_center` IDs to populate the graph's nodes.

### 3. Edge Aggregation (The Corridors)
* **Edges** represent the physical highway routes (corridors) between two facilities.
* We collapse all rows that share the exact same `(source_center, destination_center)` pair into a single directed edge. 
* This prevents the graph from having thousands of overlapping edges for the same route.

### 4. Edge Weight Calculation (Delay Ratios)
Instead of using physical distance, edge weights reflect **network friction**.
* For each aggregated edge, we calculate the median delay ratio: `segment_actual_time / segment_osrm_time`.
* A ratio > 1.0 indicates a corridor that systematically takes longer than the OSRM routing engine expects (e.g., due to traffic, poor roads, or facility dwell time).
* *Stratification:* Edges are further stratified by `route_type` (FTL vs. Carting) and `time_of_day`, as a corridor's delay profile changes dynamically based on these constraints.

### 5. Network Metrics Generation
Once the directed, weighted graph is initialized in `NetworkX`, we compute structural features to identify systemic vulnerabilities:
* **Betweenness Centrality:** Identifies bottleneck hubs that act as critical bridges in the network.
* **In/Out-Degree:** Measures facility throughput and congestion risk.
* **Clustering Coefficients:** Detects highly localized routing zones.
These metrics are then exported to serve as structural features for the downstream GraphSAGE neural network and XGBoost route-selection models.
