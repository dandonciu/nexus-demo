import streamlit as st
import time
from datetime import datetime
import math
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NEXUS B2B", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    .stSelectbox label, .stNumberInput label { font-size: 1.1rem !important; font-weight: bold !important; color: #003366 !important; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZARE VARIABILE GLOBALE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if 'order_number' not in st.session_state:
    st.session_state.order_number = 1001

# ID dinamic pentru a forța resetarea widgeturilor fără erori roșii
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

def force_reset():
    st.session_state.reset_counter += 1

if 'db' not in st.session_state:
    st.session_state.db = {
        "Role Autocut Albe TAD 220m": {
            "cod_master": "MST-BKTp721", "cod_nir": "NIR-4451",
            "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 3, "stock_box": 0, "conversion": 64,
            "descriere": "Role din celuloză pură 100%, 2 straturi, destinate dispenserelor auto-cut. Greutate palet: 210kg.",
            "livrari_totale": pd.DataFrame({
                "Client": [
                    "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL",
                    " ├─ Filiala București Nord", " ├─ Filiala București Nord", " ├─ Filiala București Nord", " ├─ Filiala București Nord",
                    " ├─ Filiala Cluj
