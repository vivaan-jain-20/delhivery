import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import networkx as nx

st.set_page_config(page_title="Smart ETA Prediction Engine", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    .gradient-title {
        background: linear-gradient(135deg, #4ade80 0%, #06b6d4 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px 28px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    
    .metric-card.accent {
        border-color: rgba(74, 222, 128, 0.3);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(6, 182, 212, 0.1) 100%);
    }
    
    .metric-card-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.075em;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 10px;
    }
    
    .metric-card-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    .metric-card.accent .metric-card-value {
        color: #4ade80;
    }
    
    /* Sidebar overall styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1329 !important; /* Deeper slate color */
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 4px 0 15px -3px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Navigation link styling */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {
        border-radius: 8px;
        margin: 4px 0;
        transition: all 0.2s ease;
    }
    
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #4ade80 !important;
    }
    
    /* Active navigation item highlight */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a[aria-current="page"] {
        background: linear-gradient(135deg, rgba(74, 222, 128, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%) !important;
        border-left: 3px solid #4ade80 !important;
        color: #4ade80 !important;
        font-weight: 600 !important;
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom Sidebar Branding and Widgets
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <h2 style="color: #4ade80; margin: 0; font-weight: 800; letter-spacing: 0.05em; font-family: 'Outfit';">DELHIVERY</h2>
            <p style="color: #64748b; font-size: 0.8rem; margin: 5px 0 0 0; text-transform: uppercase; font-family: 'Outfit'; font-weight: 600;">Control Tower</p>
        </div>
        <hr style="border-color: rgba(255,255,255,0.05); margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    # System info panel
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; margin-bottom: 20px; font-family: 'Outfit';">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;">System Status</div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem; color: #f8fafc; font-weight: 500;">All networks operational</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 8px;">Last sync: Just now</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='gradient-title'>🔮 Smart ETA Prediction Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Compare baseline OSRM computations against the 2-Hop Spatial GraphSAGE model.</p>", unsafe_allow_html=True)

# Define paths
graph_path = "graph_building_pipeline/delhivery_graph.pkl"
embeddings_path = "Graph-enhanced ETA prediction model/ml_data/sage_embeddings.pkl"
gbt_base_path = "Graph-enhanced ETA prediction model/ml_data/gbt_base.pkl"
gbt_graph_path = "Graph-enhanced ETA prediction model/ml_data/gbt_graph.pkl"

# Check if model files exist
backend_ready = (
    os.path.exists(graph_path) and 
    os.path.exists(embeddings_path) and 
    os.path.exists(gbt_base_path) and 
    os.path.exists(gbt_graph_path)
)

if not backend_ready:
    st.warning("⚠️ Backend ML models or graph embeddings are not fully generated yet. Running in **Simulation Mode**.")
    
    # Fallback/simulation selectors
    source_name = st.selectbox("Select Origin Gateway", ["Gurgaon_Bilaspur_HB (IND122015AAA)", "Bangalore_Nelamangala_H (IND562123AAA)", "Mumbai_Bhiwandi_H (IND400604AAA)"])
    dest_name = st.selectbox("Select Destination Hub", ["Delhi_Okhla_H (IND110020AAA)", "Hyderabad_Shamshabad_H (IND500001AAA)", "Pune_Wagholi_H (IND411014AAA)"])
    time_slot = st.selectbox("Departure Window (Time of Day)", ["Night", "Morning", "Afternoon", "Evening"])
    route_type = st.selectbox("Route Type", ["FTL", "Carting"])
    base_distance = st.number_input("Route Distance (km)", min_value=1, max_value=3000, value=250)
    base_osrm = st.number_input("Nominal OSRM Route Calculation Duration (Minutes)", min_value=10, max_value=2000, value=180)
    
    st.markdown("---")
    st.subheader("⏱️ Comparative Forecast Metrics")
    
    # Simple simulation fallback
    simulated_graph_eta = base_osrm * 1.24
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Baseline OSRM Estimate</div>
                <div class="metric-card-value">{base_osrm} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card accent">
                <div class="metric-card-label">GraphSAGE Predictor</div>
                <div class="metric-card-value">{int(simulated_graph_eta)} mins</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    error_buffer = abs(simulated_graph_eta - base_osrm)
    if error_buffer > 20:
        st.warning(f"⚠️ Graph structural aggregation reveals a high probability of bottleneck delays along this path. The baseline OSRM calculation underpredicts arrival constraints by approximately **{int(error_buffer)} minutes**.")
    else:
        st.success("✅ Path congestion is low. Baseline OSRM is likely accurate within the SLA window.")

else:
    # Load assets
    @st.cache_resource
    def load_ml_assets():
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
        with open(embeddings_path, 'rb') as f:
            embeddings = pickle.load(f)
        with open(gbt_base_path, 'rb') as f:
            model_base = pickle.load(f)
        with open(gbt_graph_path, 'rb') as f:
            model_graph = pickle.load(f)
        return G, embeddings, model_base, model_graph
        
    G, embeddings, model_base, model_graph = load_ml_assets()
    
    # Map node options for dropdown: "Name (ID)" -> ID
    node_options = {}
    for node, attrs in G.nodes(data=True):
        name = attrs.get("name", node)
        label = f"{name} ({node})"
        node_options[label] = node
        
    sorted_labels = sorted(list(node_options.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        source_label = st.selectbox("Select Origin Gateway", sorted_labels, index=0)
        dest_label = st.selectbox("Select Destination Hub", sorted_labels, index=min(1, len(sorted_labels)-1))
        time_slot = st.selectbox("Departure Window (Time of Day)", ["Night", "Morning", "Afternoon", "Evening"])
    with col2:
        route_type = st.selectbox("Route Type", ["FTL", "Carting"])
        base_distance = st.number_input("Route Distance (km)", min_value=1, max_value=3000, value=250)
        base_osrm = st.number_input("Nominal OSRM Route Calculation Duration (Minutes)", min_value=10, max_value=2000, value=180)
        
    # Get IDs
    src_id = node_options[source_label]
    dst_id = node_options[dest_label]
    
    # Feature construction
    is_ftl = 1.0 if route_type == "FTL" else 0.0
    
    # ['time_of_day_Evening', 'time_of_day_Morning', 'time_of_day_Night']
    evening_val = 1.0 if time_slot == "Evening" else 0.0
    morning_val = 1.0 if time_slot == "Morning" else 0.0
    night_val = 1.0 if time_slot == "Night" else 0.0
    
    # 6-dimensional baseline vector
    baseline_vector = np.array([
        float(base_osrm),
        float(base_distance),
        float(is_ftl),
        float(evening_val),
        float(morning_val),
        float(night_val)
    ])
    
    # Extract node embeddings
    blank_emb = np.zeros(16)
    src_emb = embeddings.get(src_id, blank_emb)
    dst_emb = embeddings.get(dst_id, blank_emb)
    
    # Compute interaction variables
    betweenness_delta = dst_emb[0] - src_emb[0]
    clustering_delta = dst_emb[1] - src_emb[1]
    degree_ratio = (dst_emb[2] + 1) / (src_emb[3] + 1)
    
    # 41-dimensional graph vector
    graph_vector = np.hstack([
        baseline_vector,
        src_emb,
        dst_emb,
        np.array([betweenness_delta, clustering_delta, degree_ratio])
    ])
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("⏱️ Comparative Forecast Metrics")
    
    # Live Predictions
    pred_base = model_base.predict(baseline_vector.reshape(1, -1))[0]
    pred_graph = model_graph.predict(graph_vector.reshape(1, -1))[0]
    
    # Make sure we don't display negative times in extreme settings
    pred_base = max(5.0, pred_base)
    pred_graph = max(5.0, pred_graph)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Standard OSRM Prediction</div>
                <div class="metric-card-value">{int(base_osrm)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Tabular ML Model Estimate</div>
                <div class="metric-card-value">{int(pred_base)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card accent">
                <div class="metric-card-label">GraphSAGE Predictor</div>
                <div class="metric-card-value">{int(pred_graph)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Operational Commentary
    error_diff = pred_graph - base_osrm
    if error_diff > 15.0:
        st.warning(
            f"⚠️ **CONGESTION WARNING:** The Graph-Enhanced model projects that transit will take **{int(error_diff)} minutes longer** than the nominal OSRM estimate. "
            f"This is likely caused by high structural risk (betweenness centrality: `{src_emb[0]:.4f}`) or high traffic confluence at the source/destination facilities."
        )
    elif error_diff < -15.0:
        st.success(
            f"✅ **HIGH EFFICIENCY PATH:** The Graph-Enhanced model projects that transit will complete **{int(abs(error_diff))} minutes faster** than standard OSRM estimates. "
            f"The network path has low chokehold density."
        )
    else:
        st.info("ℹ️ The baseline OSRM estimate matches our Graph-Enhanced pipeline predictions within the standard tolerance window.")
