import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Delhivery Network Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected CSS for custom branding, premium card styling, and sidebar beautification
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
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Premium glassmorphic metric cards */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px 28px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(74, 222, 128, 0.4);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 15px rgba(74, 222, 128, 0.1);
    }
    
    /* Make metric label look high-tech */
    div[data-testid="stMetricLabel"] p {
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.075em;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    
    /* Make metric value stand out */
    div[data-testid="stMetricValue"] div {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
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
    
    /* Map Container Styling */
    .map-container {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
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

st.markdown("<h1 class='gradient-title'>📊 Delhivery Logistics Network Optimizer</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Global Network Health Monitoring & Interactive Delay Risk Map</p>", unsafe_allow_html=True)

# High-level KPIs
col1, col2, col3 = st.columns(3)
col1.metric(label="Systemic SLA Breach Rate", value="14.2%", delta="-2.1%")
col2.metric(label="Total Daily Active Trips", value="114,820", delta="+5.4%")
col3.metric(label="Revenue-at-Risk Identified", value="₹4.2M", delta="-₹1.1M")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

st.subheader("🗺️ Live Geospatial Topology Map")
st.markdown("Facility size reflects *Betweenness Centrality* (chokehold risk). Corridor lines are color-coded by *Delay Ratio* (Green is optimal, Red is high SLA risk).")

# Render the interactive Folium map
map_path = "graph_visualizations/delhivery_geo_network.html"

if os.path.exists(map_path):
    with open(map_path, 'r', encoding='utf-8') as f:
        html_data = f.read()
    
    st.markdown("<div class='map-container'>", unsafe_allow_html=True)
    components.html(html_data, height=650, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Geospatial map asset pending. Run `visualize_geo.py` in the backend to render the live topology map here.")
