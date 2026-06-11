import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import networkx as nx

st.set_page_config(page_title="Fleet Routing Matrix (FTL vs. Carting)", layout="wide")

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
        border-color: rgba(6, 182, 212, 0.3);
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
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    .metric-card.accent .metric-card-value {
        color: #06b6d4;
    }
    
    /* Recommendations */
    .rec-box {
        padding: 25px;
        border-radius: 16px;
        border: 1px solid;
        margin-top: 20px;
    }
    
    .rec-box.success {
        background: rgba(74, 222, 128, 0.08);
        border-color: rgba(74, 222, 128, 0.3);
        color: #f8fafc;
    }
    
    .rec-box.info {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.3);
        color: #f8fafc;
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

st.markdown("<h1 class='gradient-title'>🚛 Fleet Routing Matrix (FTL vs. Carting)</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Evaluate counterfactual routing decisions based on distance, time of day, and source hub structural risk.</p>", unsafe_allow_html=True)

# Define paths
graph_path = "graph_building_pipeline/delhivery_graph.pkl"
embeddings_path = "Graph-enhanced ETA prediction model/ml_data/sage_embeddings.pkl"
gbt_graph_path = "Graph-enhanced ETA prediction model/ml_data/gbt_graph.pkl"

# Check if model files exist
backend_ready = (
    os.path.exists(graph_path) and 
    os.path.exists(embeddings_path) and 
    os.path.exists(gbt_graph_path)
)

if not backend_ready:
    st.warning("⚠️ Backend ML models or graph embeddings are not fully generated yet. Running in **Simulation Mode**.")
    
    col1, col2 = st.columns(2)
    with col1:
        source_risk = st.selectbox("Source Hub Structural Risk Profile", ["Low (Local Hub)", "Medium (Regional Center)", "High (National Gateway)"])
        time_of_day = st.selectbox("Dispatch Time", ["Morning", "Afternoon", "Evening", "Night"])
    with col2:
        route_distance = st.slider("Route Distance (km)", 10, 2000, 450)
        base_ftl_time = st.number_input("Standard FTL Predicted Time (Minutes)", 30, 3000, 600)

    # Carting Logic Simulation
    risk_multiplier = {"Low (Local Hub)": 1.0, "Medium (Regional Center)": 1.15, "High (National Gateway)": 1.35}
    carting_time_saved = (base_ftl_time * 0.20) * risk_multiplier[source_risk]
    carting_time = base_ftl_time - carting_time_saved
    percent_reduction = (carting_time_saved / base_ftl_time) * 100

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("📊 Scenario Simulation Results")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Standard FTL Transit</div>
                <div class="metric-card-value">{int(base_ftl_time)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Agile Carting Transit</div>
                <div class="metric-card-value">{int(carting_time)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card accent">
                <div class="metric-card-label">Absolute Time Saved</div>
                <div class="metric-card-value">{int(carting_time_saved)} mins ({percent_reduction:.1f}%)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if carting_time_saved > 10 and percent_reduction > 15.0:
        st.markdown(f"""
            <div class="rec-box success">
                <h4 style="margin:0 0 10px 0; color: #4ade80; display:flex; align-items:center; gap:8px;">
                    🎯 RECOMMENDATION: DEPLOY AGILE CARTING
                </h4>
                <p style="margin:0; font-size:0.95rem; color:#cbd5e1;">
                    The agile premium is justified. Time savings clear the 10-minute absolute hurdle and the 15% relative SLA preservation threshold.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="rec-box info">
                <h4 style="margin:0 0 10px 0; color: #3b82f6; display:flex; align-items:center; gap:8px;">
                    📦 RECOMMENDATION: DEFAULT TO BULK FTL
                </h4>
                <p style="margin:0; font-size:0.95rem; color:#cbd5e1;">
                    Carting does not provide sufficient temporal advantage to clear the financial hurdle. Utilize standard full-truckload routing to optimize unit economics.
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    @st.cache_resource
    def load_ml_assets():
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
        with open(embeddings_path, 'rb') as f:
            embeddings = pickle.load(f)
        with open(gbt_graph_path, 'rb') as f:
            model_graph = pickle.load(f)
        return G, embeddings, model_graph
        
    G, embeddings, model_graph = load_ml_assets()
    
    # Pre-calculate betweenness thresholds for risk levels (Low, Medium, High)
    all_betweenness = [embeddings.get(node, np.zeros(16))[0] for node in G.nodes]
    if len(all_betweenness) > 0:
        p25 = np.percentile(all_betweenness, 25)
        p75 = np.percentile(all_betweenness, 75)
    else:
        p25, p75 = 0.005, 0.02
        
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
        route_distance = st.slider("Route Distance (km)", 10, 2000, 450)
        base_osrm = st.number_input("Nominal OSRM Route Calculation Duration (Minutes)", min_value=10, max_value=2000, value=180)
        
    # Get IDs
    src_id = node_options[source_label]
    dst_id = node_options[dest_label]
    
    # Extract node embeddings
    blank_emb = np.zeros(16)
    src_emb = embeddings.get(src_id, blank_emb)
    dst_emb = embeddings.get(dst_id, blank_emb)
    
    # Determine risk category dynamically
    src_bet = src_emb[0]
    if src_bet <= p25:
        risk_level = "Low (Local Hub)"
    elif src_bet >= p75:
        risk_level = "High (National Gateway)"
    else:
        risk_level = "Medium (Regional Center)"
        
    st.info(f"ℹ️ **Source Hub Risk Profile:** `{risk_level}` (Betweenness Centrality: `{src_bet:.6f}`)")
    
    # ['time_of_day_Evening', 'time_of_day_Morning', 'time_of_day_Night']
    evening_val = 1.0 if time_slot == "Evening" else 0.0
    morning_val = 1.0 if time_slot == "Morning" else 0.0
    night_val = 1.0 if time_slot == "Night" else 0.0
    
    # Construct base feature vectors for FTL and Carting
    ftl_baseline = np.array([float(base_osrm), float(route_distance), 1.0, float(evening_val), float(morning_val), float(night_val)])
    carting_baseline = np.array([float(base_osrm), float(route_distance), 0.0, float(evening_val), float(morning_val), float(night_val)])
    
    # Compute interaction variables
    betweenness_delta = dst_emb[0] - src_emb[0]
    clustering_delta = dst_emb[1] - src_emb[1]
    degree_ratio = (dst_emb[2] + 1) / (src_emb[3] + 1)
    
    # 41-dimensional graph vectors
    ftl_vector = np.hstack([ftl_baseline, src_emb, dst_emb, np.array([betweenness_delta, clustering_delta, degree_ratio])])
    carting_vector = np.hstack([carting_baseline, src_emb, dst_emb, np.array([betweenness_delta, clustering_delta, degree_ratio])])
    
    # Live Predictions
    predicted_time_ftl = max(5.0, model_graph.predict(ftl_vector.reshape(1, -1))[0])
    predicted_time_carting = max(5.0, model_graph.predict(carting_vector.reshape(1, -1))[0])
    
    # Calculate savings
    carting_time_saved = predicted_time_ftl - predicted_time_carting
    percent_reduction = (carting_time_saved / predicted_time_ftl) * 100
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("📊 Scenario Simulation Results")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Standard FTL Predicted Time</div>
                <div class="metric-card-value">{int(predicted_time_ftl)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Agile Carting Predicted Time</div>
                <div class="metric-card-value">{int(predicted_time_carting)} mins</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        if carting_time_saved > 0:
            st.markdown(f"""
                <div class="metric-card accent">
                    <div class="metric-card-label">Absolute Time Saved</div>
                    <div class="metric-card-value">{int(carting_time_saved)} mins ({percent_reduction:.1f}%)</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="metric-card accent" style="border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.05);">
                    <div class="metric-card-label">Absolute Time Saved</div>
                    <div class="metric-card-value" style="color: #ef4444;">0 mins (0.0%)</div>
                </div>
            """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if carting_time_saved > 10.0 and percent_reduction > 15.0:
        st.markdown(f"""
            <div class="rec-box success">
                <h4 style="margin:0 0 10px 0; color: #4ade80; display:flex; align-items:center; gap:8px;">
                    🎯 RECOMMENDATION: DEPLOY AGILE CARTING
                </h4>
                <p style="margin:0; font-size:0.95rem; color:#cbd5e1;">
                    The agile premium is justified. Time savings clear the 10-minute absolute hurdle and the 15% relative SLA preservation threshold.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="rec-box info">
                <h4 style="margin:0 0 10px 0; color: #3b82f6; display:flex; align-items:center; gap:8px;">
                    📦 RECOMMENDATION: DEFAULT TO BULK FTL
                </h4>
                <p style="margin:0; font-size:0.95rem; color:#cbd5e1;">
                    Carting does not provide sufficient temporal advantage to justify the premium cost. Utilize standard full-truckload routing to optimize unit economics.
                </p>
            </div>
        """, unsafe_allow_html=True)
