import streamlit as st
import pandas as pd
import plotly.express as px
from backend.database.clients_config import clients_data

def render_manager_dashboard():
    st.title("📈 NEXUS Dashboard Manager")
    
    st.subheader("1. Privire de Ansamblu")
    c_k1, c_k2, c_k3 = st.columns(3)
    c_k1.success("Livrări în grafic (Azi): 4")
    c_k2.warning("Recepții în așteptare (SmartBill): 1")
    c_k3.error("Facturi restante clienți: 2")
    st.divider()
    
    st.subheader("2. Analiză WMS Punctual")
    mgr_prod = st.selectbox("Selectare Produs:", list(st.session_state.db.keys()))
    p_val = st.session_state.db[mgr_prod]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paleți Intacți", p_val['stock_pal'])
    c2.metric("Cutii Libere", p_val['stock_box'])
    c3.metric("Conversie WMS", f"{p_val['conversion']} cutii/palet")
    c4.metric("Conversie Fiscală", f"{p_val['conversie_baza']} {p_val['um_baza']}/cutie")
            
    st.divider()
    st.subheader("3. Istoric Livrări (Grafic)")
    col_m1, col_m2 = st.columns([2, 2])
    with col_m1: analiza_client = st.selectbox("Selectează Client:", list(clients_data.keys()))
    with col_m2: analiza_produs = st.selectbox("Selectează Produs pt. istoric:", list(st.session_state.db.keys()), key="mgr_prod_an")
    
    # Preluare istoric de livrări din baza de date centrală
    df_toate = st.session_state.db[analiza_produs].get("livrari_totale", pd.DataFrame())
    
    # Verificăm dacă avem date pentru clientul selectat
    if not df_toate.empty:
        df_filtrat = df_toate[df_toate['Client'] == analiza_client]
    else:
        df_filtrat = pd.DataFrame()
    
    if df_filtrat.empty:
        st.warning(f"Nu există date de livrare pentru {analiza_produs} către {analiza_client}.")
    else:
        fig = px.bar(
            df_filtrat, 
            x='Data', 
            y='Volum_Paleti', 
            color='Status_Plata', 
            text='Volum_Paleti', 
            title=f"Volum Livrări: {analiza_produs} -> {analiza_client}",
            color_discrete_map={'Achitat': '#28a745', 'În termen': '#17a2b8', 'Restanță': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)
