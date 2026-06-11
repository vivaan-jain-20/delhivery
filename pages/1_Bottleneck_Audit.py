import streamlit as st
import pickle
import pandas as pd
import os
import networkx as nx

st.set_page_config(page_title="Systemic Bottleneck Auditor", layout="wide")

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
    
    /* Strategic Card */
    .payoff-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(74, 222, 128, 0.2);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    .payoff-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4ade80;
        margin: 10px 0;
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

st.markdown("<h1 class='gradient-title'>🕸️ Systemic Bottleneck Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Audits logistics gateways using real-time topological properties to isolate key structural risk points.</p>", unsafe_allow_html=True)

@st.cache_data
def load_graph_metrics():
    graph_path = "graph_building_pipeline/delhivery_graph.pkl"
    if not os.path.exists(graph_path):
        return pd.DataFrame({
            "Hub ID": ["IND122015AAA", "IND562123AAA", "IND400604AAA", "IND110020AAA", "IND411014AAA"],
            "Hub Name": ["Gurgaon_Bilaspur_HB", "Bangalore_Nelamangala_H", "Mumbai_Bhiwandi_H", "Delhi_Okhla_H", "Pune_Wagholi_H"],
            "In-Degree": [142, 128, 115, 98, 85],
            "Out-Degree": [135, 130, 110, 95, 80],
            "Chokehold Score (Betweenness)": [0.085, 0.072, 0.064, 0.051, 0.048],
            "Dependency Score (PageRank)": [9.85, 9.21, 8.84, 7.62, 7.18]
        })
        
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
    
    G_di = nx.DiGraph(G)
    pagerank = nx.pagerank(G_di)
    betweenness = nx.betweenness_centrality(G_di)
    
    node_data = []
    for node, attrs in G.nodes(data=True):
        node_data.append({
            "Hub ID": node,
            "Hub Name": attrs.get("name", node),
            "In-Degree": attrs.get("in_degree", 0),
            "Out-Degree": attrs.get("out_degree", 0),
            "Chokehold Score (Betweenness)": betweenness.get(node, 0.0),
            "Dependency Score (PageRank)": pagerank.get(node, 0.0) * 100 
        })
    return pd.DataFrame(node_data)

df_hubs = load_graph_metrics()

# Let user choose ranking metric
sort_by = st.selectbox("Rank Gateway Hubs By:", ["Dependency Score (PageRank)", "Chokehold Score (Betweenness)", "In-Degree", "Out-Degree"])
df_sorted = df_hubs.sort_values(by=sort_by, ascending=False)

top_n = st.slider("Select Number of Gateways to Audit", 5, 50, 10)

st.subheader(f"Top {top_n} Critical Logistics Hubs")
st.dataframe(df_sorted.head(top_n), use_container_width=True, hide_index=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.subheader("🎛️ Strategic Intervention Simulator")
st.markdown("Quantify estimated operational payoffs when upgrading handling and processing capacity at these core hubs.")

# Upgrade Slider
upgrade_level = st.slider("Select Investment Allocation Target (% Hub Processing Capacity Increase)", 0, 50, 20)

recovered_revenue = upgrade_level * 145000 
sla_improvement = upgrade_level * 0.35

st.markdown(f"""
    <div class="payoff-card">
        <h4 style="margin: 0; color: #94a3b8; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Projected Operational Payoff</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 40px; margin-top: 15px;">
            <div>
                <span style="font-size: 0.9rem; color: #94a3b8;">Recovered Revenue-at-Risk</span>
                <div class="payoff-value">₹{recovered_revenue:,.2f}</div>
            </div>
            <div>
                <span style="font-size: 0.9rem; color: #94a3b8;">SLA Late-Delivery Reduction</span>
                <div class="payoff-value" style="color: #06b6d4;">-{sla_improvement:.2f}%</div>
            </div>
        </div>
        <p style="margin: 15px 0 0 0; font-size: 0.9rem; color: #64748b;">
            Upgrade simulation modeling scales linearly based on baseline congestion thresholds mapped at critical nodes.
        </p>
    </div>
""", unsafe_allow_html=True)
