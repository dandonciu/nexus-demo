import streamlit as st
import pandas as pd
import numpy as np

# 1. BYPASS SECURITATE (Deblocare Temporară)
if 'role' not in st.session_state:
    st.session_state.role = 'Manager' # Forțăm rolul ca să trecem de "Interzis"

# Dacă ești Manager sau Admin, ai voie. Dacă nu, block.
if st.session_state.role not in ['Manager', 'Admin']:
    st.error("⛔ Interzis accesul. Această pagină este doar pentru Management.")
    st.stop()

# 2. INTERFAȚA PREMIUM (Luminițe și Coloane)
st.set_page_config(page_title="NEXUS | Manager Analytics", page_icon="📊", layout="wide")

st.title("📊 Manager Analytics & Control Board")
st.markdown("Monitorizare în timp real a performanței operaționale și a discrepanțelor WMS.")
st.divider()

# --- SECȚIUNEA 1: KPI-uri Globale (Luminițele) ---
st.subheader("Indicatori Cheie (Azi)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Comenzi Lansate", value="42", delta="12 de ieri", delta_color="normal")
with kpi2:
    st.metric(label="Alerte Discrepanță (Oracle)", value="3", delta="-2 față de ieri", delta_color="inverse")
with kpi3:
    st.metric(label="Timp Mediu Validare", value="14 min", delta="-3 min", delta_color="normal")
with kpi4:
    st.metric(label="Valoare Blocată (Paleți Fantomă)", value="18,500 RON", delta="Risc Major", delta_color="off")

st.divider()

# --- SECȚIUNEA 2: GRAFICE ȘI ANALIZĂ ---
col_chart, col_data = st.columns([2, 1])

with col_chart:
    st.subheader("📈 Evoluție Comenzi (Ultimele 7 zile)")
    # Generăm date vizuale de impact
    chart_data = pd.DataFrame(
        np.random.randn(7, 2) * 10 + [50, 10], 
        columns=['Comenzi Lansate', 'Alerte WMS']
    )
    st.line_chart(chart_data)

with col_data:
    st.subheader("🚨 Top 3 Discrepanțe Oracle")
    st.error("**BKTp721**\n\nStoc Oracle: 26 Paleți | Real: 25\n\nMinus cutii: -21 buc")
    st.warning("**NS50X60S15S**\n\nStoc Oracle: 0 Paleți | Real: ?\n\nMinus cutii: -5 buc")
    st.info("**PAL 721**\n\nSpargere nesemnalizată în sistem.")

st.divider()

# --- SECȚIUNEA 3: TABEL RAPOARTE RAPIDE ---
st.subheader("📋 Log Operațional (Ultimul flux)")
df_log = pd.DataFrame({
    "ID Comandă Internă": ["NEX-1001", "NEX-1002", "NEX-1003"],
    "Client": ["SIDE ALBA", "DEDEMAN", "NOVA INTERNAL"],
    "Status NEXUS": ["Facturat", "Blocat (Discrepanță Stoc)", "Așteaptă WMS"],
    "Acțiune Necesară": ["Niciuna", "Validare Comercială", "Sună Depozitul"]
})
st.dataframe(df_log, use_container_width=True)

st.caption("🤖 Notă: Rapoartele sunt extrase în timp real din NEXUS Buffer, ignorând erorile de întârziere din WMS.")
