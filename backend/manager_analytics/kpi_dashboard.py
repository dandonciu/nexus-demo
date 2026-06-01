import streamlit as st
import pandas as pd
import plotly.express as px
import math

def force_inject_mock_data():
    """Simulează baza de date pentru demo. 
    FIX: Am eliminat spațiile de la finalul cheilor pentru a preveni erorile de KeyError."""
    st.session_state.db = {
        "Role Autocut Albe TAD 220m": {
            "cod_master": "MST-BKTp721", "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 3, "stock_box": 14, "conversion": 64,
            "descriere": "Role din celuloză pură 100%, 2 straturi.",
            "livrari_totale": pd.DataFrame({
                "Client": ["🏢 ALPHA SRL", " ├─ Filiala Nord", " ├─ Filiala Cluj", "🏢 BETA DIST"] * 4,
                "Data": pd.date_range("2024-01-01", periods=16, freq="20D").strftime("%d-%m-%Y"),
                "Volum_Paleti": [12, 5, 4, 20, 15, 8, 6, 25, 10, 4, 8, 18, 22, 6, 12, 30],
                "Status_Plata": ["Achitat", "Achitat", "Restanță", "În termen"] * 4
            })
        },
        "Lavete Craft Puromore Blue": {
            "cod_master": "MST-70117", "oracle_pal": "PAL 70117", "oracle_box": "70117",
            "stock_pal": 1, "stock_box": 10, "conversion": 120,
            "descriere": "Lavete industriale rezistente la solvenți.",
            "livrari_totale": pd.DataFrame({
                "Client": ["🏢 ALPHA SRL", " ├─ Filiala Nord", " ├─ Filiala Cluj", "🏢 BETA DIST"] * 2,
                "Data": pd.date_range("2024-01-01", periods=8, freq="30D").strftime("%d-%m-%Y"),
                "Volum_Paleti": [5, 2, 8, 15, 8, 4, 6, 20],
                "Status_Plata": ["Restanță", "Achitat", "În termen", "Achitat"] * 2
            })
        }
    }
    if 'istoric_comenzi_live' not in st.session_state:
        st.session_state.istoric_comenzi_live = []
    return ["🏢 ALPHA SRL", " ├─ Filiala Nord", " ├─ Filiala Cluj", "🏢 BETA DIST"]

def render_manager_dashboard():
    clients_mock = force_inject_mock_data()
    st.title("📊 NEXUS Manager Analytics")

    # === FILTRE GLOBALE ===
    col_f1, col_f2 = st.columns(2)
    with col_f1: analiza_client = st.selectbox(" Client / Filială:", ["TOȚI CLIENȚII"] + clients_mock)
    with col_f2: analiza_produs = st.selectbox("📦 Produs:", list(st.session_state.db.keys()))
    st.divider()

    df_toate = st.session_state.db[analiza_produs]["livrari_totale"]
    df_toate["Data_Obj"] = pd.to_datetime(df_toate["Data"], format="%d-%m-%Y")
    df_toate["Luna"] = df_toate["Data_Obj"].dt.to_period("M").dt.to_timestamp().dt.strftime("%b %Y")

    # Filtrare pentru graficele specifice (Luni și Istoric)
    if analiza_client != "TOI CLIENȚII":
        df_filtrat = df_toate[df_toate["Client"] == analiza_client]
    else:
        df_filtrat = df_toate

    with st.tabs(["⚡ Situație Operativă", "📊 Rapoarte & Analiză"]):

        # TAB 1: OPERATIONAL
        st.subheader(" LIVE FEED: Comenzi Noi")
        if st.session_state.istoric_comenzi_live:
            st.dataframe(pd.DataFrame(st.session_state.istoric_comenzi_live).tail(5), hide_index=True)
        else:
            st.info("Nicio comandă nouă lansată astăzi.")

        st.divider()
        st.subheader("📦 Status Stoc (WMS)")
        p = st.session_state.db[analiza_produs]
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Paleți", p["stock_pal"])
        col_s2.metric("Cutii libere", p["stock_box"])
        # Logică simplă de status
        total = (p["stock_pal"] * p["conversion"]) + p["stock_box"]
        status = "🟢 OK" if total > p["conversion"] else "🔴 Critic"
        col_s3.metric("Status", status)

        st.divider()

        # TAB 2: ANALYTICS & RAPORTĂRI
        st.subheader("📈 Rapoarte Performanță")

        # 1. GRAFIC LUNI (12 Luni vizibile)
        st.markdown("#### 📆 Volum Livrări pe Luni")
        df_luni = df_filtrat.groupby(["Luna", "Status_Plata"])["Volum_Paleti"].sum().reset_index()

        fig_luni = px.bar(df_luni, x="Luna", y="Volum_Paleti", color="Status_Plata",
                          color_discrete_map={"Achitat": "#28a745", "În termen": "#17a2b8", "Restanță": "#dc3545"},
                          title=f"{analiza_produs} → {analiza_client}")
        
        # FIX HOVER: Caseta apare doar la cursor (deasupra barei), fără text pe axa X
        fig_luni.update_layout(hovermode='closest') 
        fig_luni.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<extra></extra>")
        
        fig_luni.update_layout(xaxis_tickangle=-45, bargap=0.15, height=400) # bargap mic pt 12 luni
        st.plotly_chart(fig_luni, use_container_width=True)

        st.divider()

        # 2. GRAFIC TOP CLIENȚI (Distribuție)
        st.markdown("#### 🏆 Distribuție Volum per Client")
        df_top = df_toate.groupby("Client")["Volum_Paleti"].sum().reset_index().sort_values("Volum_Paleti", ascending=False)
        
        fig_top = px.bar(df_top, x="Client", y="Volum_Paleti", color="Volum_Paleti",
                         color_continuous_scale="Blues", title="Top Clienți (Total)")
        
        # FIX HOVER
        fig_top.update_layout(hovermode='closest')
        fig_top.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<extra></extra>")
        
        fig_top.update_layout(xaxis_tickangle=-45, bargap=0.3, height=350, coloraxis_showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

        st.divider()

        # 3. GRAFIC ISTORIC DETALIAT
        st.markdown("#### 🔎 Istoric Zilnic (Detaliu)")
        if analiza_client == "TOȚI CLIENȚII":
            st.info("💡 Pentru detalii zilnice, te rog să selectezi un anumit client.")
        elif df_filtrat.empty:
            st.warning("Nu există date pentru selecția curentă.")
        else:
            fig_detaliu = px.bar(df_filtrat, x="Data", y="Volum_Paleti", color="Status_Plata",
                                 color_discrete_map={"Achitat": "#28a745", "În termen": "#17a2b8", "Restanță": "#dc3545"},
                                 title=f"Livrări la nivel de zi - {analiza_client}")
            
            # FIX HOVER
            fig_detaliu.update_layout(hovermode='closest')
            # Afișăm data și volumul în caseta de hover
            fig_detaliu.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<br>%{x}<extra></extra>")
            
            fig_detaliu.update_layout(xaxis_tickangle=-45, bargap=0.3, height=400)
            st.plotly_chart(fig_detaliu, use_container_width=True)
