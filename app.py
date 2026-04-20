import streamlit as st
import pickle
import pandas as pd
import json
import os
from datetime import datetime

# Find the project root (works whether app.py is in root or app/ subfolder)
_this_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(_this_dir, "models")):
    BASE_DIR = _this_dir
else:
    BASE_DIR = os.path.dirname(_this_dir)

# Configure Streamlit page
st.set_page_config(
    page_title="houseprice predicition",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CYBERPUNK CSS DESIGN ---
st.markdown("""
<style>
    /* Global Cyberpunk Themes */
    [data-testid="stAppViewContainer"] {
        background-color: #06080d;
        background-image: radial-gradient(circle at 50% 0%, #0b1120, #06080d 70%);
        color: #00f3ff;
        font-family: 'JetBrains Mono', 'Courier New', Courier, monospace;
    }
    [data-testid="stHeader"] {
        background-color: rgba(6, 8, 13, 0.8) !important;
    }
    
    /* Neon Text and Glass Panels */
    .cyber-title {
        color: transparent;
        background-clip: text;
        -webkit-background-clip: text;
        background-image: linear-gradient(to right, #00f3ff, #bc13fe);
        font-size: 2.5rem;
        font-weight: bold;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    .neon-text {
        color: #00ff66;
        letter-spacing: 1px;
    }
    
    /* Login & Glass Panels */
    .glass-panel {
        background: rgba(11, 15, 25, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 10px;
        padding: 40px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
        text-align: center;
        margin-top: 50px;
    }
    
    /* Style inputs */
    div[data-baseweb="input"] > div {
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #00f3ff !important;
        color: #fff !important;
    }
    
    /* Style Buttons */
    div.stButton > button {
        background: transparent !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: rgba(0, 243, 255, 0.2) !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
        color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION LOGIC ---
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show login box
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="glass-panel">
                <h1 class="cyber-title">houseprice prediction</h1>
                <p style="color: #bc13fe; font-size: 14px; margin-bottom: 20px;">[ Establish Secure Connection to AI House Predictor ]</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Input fields inside layout
            st.text_input("ACCESS_ID", key="username", placeholder="Enter ID")
            st.text_input("SECURITY_KEY", type="password", key="password", placeholder="Enter Key")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("⚡ INITIALISE LINK", on_click=password_entered, use_container_width=True)
            
        return False
        
    elif not st.session_state["password_correct"]:
        # Wrong password
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="glass-panel" style="border-color: #ff003c; box-shadow: 0 0 20px rgba(255, 0, 60, 0.2);">
                <h1 class="cyber-title" style="background-image: linear-gradient(to right, #ff003c, #ff9900);">ACCESS DENIED</h1>
                <p style="color: #ff003c; font-size: 14px; margin-bottom: 20px;">[ Unauthorized access prohibited ]</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("ACCESS_ID", key="username")
            st.text_input("SECURITY_KEY", type="password", key="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("⚡ RETRY CONNECTION", on_click=password_entered, use_container_width=True)
        return False
        
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Stop execution until authenticated

# --- MAIN APP LOGIC ---

# === TEMPORARY DEBUG - REMOVE AFTER FIXING ===
st.sidebar.write("🔍 **DEBUG INFO**")
st.sidebar.write(f"__file__: {os.path.abspath(__file__)}")
st.sidebar.write(f"_this_dir: {_this_dir}")
st.sidebar.write(f"BASE_DIR: {BASE_DIR}")
st.sidebar.write(f"Files in _this_dir: {os.listdir(_this_dir)}")
try:
    parent = os.path.dirname(_this_dir)
    st.sidebar.write(f"Files in parent: {os.listdir(parent)}")
except:
    st.sidebar.write("Cannot list parent dir")
st.sidebar.write(f"models exists in _this_dir? {os.path.exists(os.path.join(_this_dir, 'models'))}")
st.sidebar.write(f"models exists in parent? {os.path.exists(os.path.join(os.path.dirname(_this_dir), 'models'))}")
# === END DEBUG ===

@st.cache_resource
def load_model():
    with open(os.path.join(BASE_DIR, "models", "trained_model.pkl"), "rb") as f:
        model = pickle.load(f)
    return model

@st.cache_data
def load_metadata():
    try:
        with open(os.path.join(BASE_DIR, "models", "metadata.json"), "r") as f:
            metadata = json.load(f)
        return metadata['neighborhoods']
    except FileNotFoundError:
        return ["NAmes", "CollgCr", "OldTown", "Edwards", "Somerst", "Gilbert", "NridgHt"] # Fallback

model = load_model()
neighborhoods = load_metadata()

# Header & Logout 
col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
with col1:
    st.markdown("<h1 class='cyber-title'>AI HOUSE SYSTEM <span style='font-size: 1rem; color: #00f3ff; border: 1px solid #00f3ff; padding: 2px 6px; border-radius: 4px;'>v2.0.4</span></h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<div style='text-align: right; padding-top: 15px;'><span class='neon-text'>● MODEL: LOADED</span> &nbsp;&nbsp; <span style='color: #00f3ff;'>● SYSTEM: ACTIVE</span></div>", unsafe_allow_html=True)
with col3:
    if st.button("TERMINATE"):
        st.session_state["password_correct"] = False
        st.rerun()

st.markdown("<hr style='border: 1px solid rgba(0, 243, 255, 0.2);'>", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='color: #bc13fe;'>[ INPUT_PARAMETERS ]</h3>", unsafe_allow_html=True)
    overall_qual = st.slider("OVERALL QUALITY (1-10)", 1, 10, 5)
    gr_liv_area = st.number_input("LIVING AREA (SQ FT)", min_value=500, max_value=5000, value=1500)
    neighborhood = st.selectbox("NEIGHBORHOOD_ZONE", neighborhoods)
    year_built = st.number_input("YEAR BUILT", min_value=1800, max_value=datetime.now().year, value=2000)

with col2:
    st.markdown("<h3 style='color: #bc13fe;'>[ SECONDARY_METRICS ]</h3>", unsafe_allow_html=True)
    total_bsmt_sf = st.number_input("BASEMENT AREA (SQ FT)", min_value=0, max_value=3000, value=1000)
    first_flr_sf = st.number_input("1ST FLOOR AREA (SQ FT)", min_value=300, max_value=4000, value=1000)
    second_flr_sf = st.number_input("2ND FLOOR AREA (SQ FT)", min_value=0, max_value=3000, value=500)
    full_bath = st.slider("FULL BATHROOMS", 0, 5, 2)
    garage_cars = st.slider("GARAGE CAPACITY (CARS)", 0, 5, 2)
    garage_area = st.number_input("GARAGE AREA (SQ FT)", min_value=0, max_value=1500, value=500)
    year_remod_add = st.number_input("YEAR REMODELED", min_value=1900, max_value=datetime.now().year, value=2005)

st.markdown("<hr style='border: 1px solid rgba(0, 243, 255, 0.2);'>", unsafe_allow_html=True)

# Prediction Button & Output
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("⚡ EXECUTE VALUATION SCAN", use_container_width=True):
        input_data = pd.DataFrame([{
            'OverallQual': overall_qual,
            'GrLivArea': gr_liv_area,
            'GarageCars': garage_cars,
            'GarageArea': garage_area,
            'TotalBsmtSF': total_bsmt_sf,
            '1stFlrSF': first_flr_sf,
            '2ndFlrSF': second_flr_sf,
            'FullBath': full_bath,
            'YearBuilt': year_built,
            'YearRemodAdd': year_remod_add,
            'Neighborhood': neighborhood
        }])
        
        input_data['TotalArea'] = input_data['TotalBsmtSF'] + input_data['1stFlrSF'] + input_data['2ndFlrSF']
        input_data['HouseAge'] = datetime.now().year - input_data['YearBuilt']
        
        with st.spinner("Analyzing neural streams through XGBoost..."):
            prediction = model.predict(input_data)[0]
        
        st.markdown(f"""
        <div class="glass-panel" style="margin-top: 10px;">
            <p style="color: #00f3ff; font-weight: bold; font-size: 12px; letter-spacing: 3px;">ESTIMATED VALUATION CONVERGED</p>
            <h1 style="color: #00ff66; font-size: 4rem; text-shadow: 0 0 20px rgba(0, 255, 102, 0.5);">${prediction:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
