#  Graph-Enhanced Gradient Boosting ETA Engine & Route Optimizer

This directory houses the machine learning and simulation components of the logistics transit pipeline. It ingests the structured network assets produced by the upstream data pipeline (`/cleaning` and `/graph_building_pipeline`), extracts high-dimensional spatial topology features using Graph Neural Network (GNN) neighborhood concepts, and executes a high-speed head-to-head evaluation benchmark. 

Additionally, it deploys a **Digital Twin counterfactual simulation framework** to quantify time-cost trade-offs for route-type selections (FTL vs. Carting).

---

##  Architectural Overview

Traditional transportation routing frameworks analyze travel corridors exclusively using standalone segment attributes (e.g., OSRM distance baseline, nominal highway speed limits). This architecture enhances tabular trip details by infusing a **2-Hop Spatial Neighborhood Aggregator** inspired by the GraphSAGE framework, optimizing the mapping phase using state-of-the-art Histogram Gradient Boosting.

### 1. Structural Metric Foundations
The pipeline evaluates fundamental graph-theoretic patterns for each logistics facility node across the transit network topology:
* **PageRank Centrality**: Rapidly flags major systemic bottleneck hubs by calculating network path confluence and relative node importance using power-iteration matrices.
* **Clustering Coefficient**: Measures localized network transit redundancy and cluster density.
* **In/Out-Degree**: Quantifies instantaneous corridor capacity, volume handling, and path convergence traits.

### 2. Deep 2-Hop Neighborhood Aggregation
To explicitly model network constraints that extend beyond individual starting and ending nodes, a spatial message-passing routine aggregates contextual layout structures:
* **1-Hop Ingestion**: Nodes pull in the structural feature traits of their immediate adjacent successors using a mean-pooling aggregation function.
* **2-Hop Ingestion**: Nodes repeat the aggregation loop over their expanded neighborhood horizon, generating a 16-dimensional spatial fingerprint that implicitly captures multi-step downstream congestion risks.

### 3. Topological Corridor Interaction Dynamics
To expose transitional network behavior across trip paths, the script maps edge arrays using interaction delta layers:
* **Centrality Deltas**: $\text{PageRank}_{\text{Destination}} - \text{PageRank}_{\text{Source}}$ (Models systemic structural shifts).
* **Network Clustering Deltas**: $\text{Clustering}_{\text{Destination}} - \text{Clustering}_{\text{Source}}$ (Models shifts in localized layout density).
* **Hub Processing Ratio**: $\frac{\text{In-Degree}_{\text{Destination}} + 1}{\text{Out-Degree}_{\text{Source}} + 1}$ (Quantifies bottleneck constraints at downstream nodes).

### 4. High-Speed Histogram Gradient Boosting
While traditional Random Forest estimators scale poorly when calculating Mean Absolute Error (MAE) criteria over large matrices—requiring repetitive, expensive data sorting steps at every split—this engine deploys `HistGradientBoostingRegressor`. 
* **The Histogram Secret**: It bins continuous input features into 256 discrete integer intervals. This maps continuous columns into fast, structured histograms, cutting compute times on the 114k row dataset from **over an hour down to under 15 seconds**.
* **Sequential Ensemble Learning**: Rather than calculating isolated trees, trees are grown sequentially, directly adapting to correct residual absolute error variations from previous branches to minimize loss targets.

---

##  ML-Backed FTL vs. Carting Decision Framework

Rather than treating the vehicle deployment type (`is_ftl`) as a static historical data point, the framework evaluates routing strategies via a **Counterfactual Scenario Simulator**. 

### 1. The Core Simulation Engine
The system clones the active testing dataset and sets up parallel routing options for the exact same trips under the same time-of-day and network congestion settings. It forces one matrix entirely to Full Truck Load (FTL = 1.0) and the other entirely to Carting (Carting = 0.0), calculating the exact time delta gap:
$$\text{Time Saved by Carting} = \text{Predicted Time}_{\text{FTL}} - \text{Predicted Time}_{\text{Carting}}$$

### 2. Operational Heuristic Constraints
Because agile Carting routes require an increased financial premium from Delhivery's operational budget, the system applies an absolute and relative filtering hurdle to prevent financial waste on negligible micro-savings:
* **The Hurdle Rule**: Carting is recommended **ONLY** if it saves **more than 10 minutes** of absolute transit time **AND** reduces the journey duration by **more than 15%** (directly preserving the strict 15% SLA accuracy window). 
* **The Default**: If a trip profile falls short of this threshold, the engine automatically defaults to standard, cost-efficient bulk FTL.

### 3. Topological Risk Profiling
By pairing distance clusters with the source hub's **Betweenness Centrality**, the output proves mathematically how facility risk affects fleet efficiency. This provides dispatch teams with a clear playbook: pay the premium for Carting on short/mid-haul trips leaving high-risk gateways to bypass queuing delays, while standardizing long-hauls through cheap bulk FTL.

---

##  Repository Components

* **`prepare_ml_data.py`**: Interacts dynamically with adjacent project directories to construct deep neighborhood embeddings, calculates interaction profiles, and serializes optimized numeric (`float64`) training arrays into the cache folder.
* **`train_models.py`**: A high-efficiency benchmarking script that loads cached feature matrices, executes parallelized histogram boosting optimization, and prints out the final baseline vs. graph-enhanced performance scoreboard.
* **`route_optimization_framework.py`**: The simulation brain that reads cached numpy arrays, evaluates counterfactual FTL vs. Carting scenarios, groups corridors by haul profiles, filters for structural hub risks, and outputs strategic routing recommendations.

---



