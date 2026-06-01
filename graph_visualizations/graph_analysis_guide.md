# Geospatial Network Graph: Feature Analysis & Strategy Guide

This document outlines the visual features encoded within the `delhivery_geo_network.html` interactive map and provides a framework for translating these visuals into actionable business insights for the Strategy Memo.

---

## 1. The Hubs (Nodes / Circles)
Every circle on the map represents a distinct Delhivery facility. The visual styling of these hubs instantly reveals their structural risk to the national network.

### Size (Radius)
* **What it represents:** Betweenness Centrality (Chokehold Risk).
* **How to observe it:** The larger the circle, the more critical that facility is as a "bridge" in the network. A massive circle indicates that a high percentage of all shortest paths across the country *must* pass through this exact hub.

### Color Gradient (Blue → Purple → Pink)
* **What it represents:** Also maps to Betweenness Centrality (visually reinforcing the node size).
* **How to observe it:** 
  * **Blue:** Local end-points or minor branches. 
  * **Deep Purple / Bright Pink:** The absolute center of the logistics web. If a pink hub goes down, the entire national network experiences a ripple effect.

### Hover Tooltip & Click Popup
* **What it represents:** Raw operational metrics.
* **How to observe it:** 
  * **Hover:** View the facility name. 
  * **Click:** Open the popup panel to read exact metrics, including the **In-Degree** (number of facilities sending trucks *to* it) and **Out-Degree** (number of facilities it sends trucks *to*).

---

## 2. The Corridors (Edges / Lines)
Every line connecting two hubs represents a specific logistical route execution (e.g., FTL trucks driving at Night).

### Line Color (Green → Yellow → Red)
* **What it represents:** The Median Delay Ratio (Actual Time / OSRM Time).
* **How to observe it:** 
  * **Green (Ratio ≤ 1.0):** Highly efficient corridors where actual delivery times match or beat the OSRM prediction.
  * **Yellow (Ratio 1.1 - 1.4):** Minor friction. Vehicles are taking slightly longer than predicted.
  * **Bright Red (Ratio ≥ 1.5):** Severe, chronic delays. The actual drive/dwell time is taking 50%+ longer than the system expects.

### Line Thickness
* **What it represents:** Traffic Volume (`total_trips`).
* **How to observe it:** A thin line represents a rarely used route (e.g., 6 trips). A thick line represents a heavily trafficked, primary highway corridor.

### Hover Tooltip
* **What it represents:** Specific route constraints.
* **How to observe it:** Hover over any line to see the exact edge profile. The tooltip details if the line represents **FTL** or **Carting**, the **Time of Day** it occurs, and the exact delay multiplier. *(Note: Multiple parallel lines may exist between the same two cities representing different profiles).*

---

## 3. Strategy Memo Application: The "Hunt"
To generate targeted recommendations for the Strategy Memo, zoom out to view the entire country and look for overlapping visual cues that define a **Danger Zone**.

### Defining a Danger Zone
A critical bottleneck is visually defined by two elements occurring together:
1. **A massive, pink node** (High structural importance / Betweenness Centrality).
2. **Surrounded by thick, bright red lines** (High volume, severe SLA delays).

### Formulating the Recommendation
When this pattern is identified:
1. Zoom in and click the hub to identify its exact name and ID (e.g., `Gurgaon_Bilaspur_HB`).
2. Hover over the incoming/outgoing red lines to diagnose the specific failure (e.g., Are delays only happening for FTL trucks at Night?).
3. Draft a targeted intervention in the Strategy Memo. For example: *Recommend upgrading the night-shift processing capacity at Gurgaon_Bilaspur_HB or rerouting Carting traffic to bypass this hub entirely during peak hours.*
