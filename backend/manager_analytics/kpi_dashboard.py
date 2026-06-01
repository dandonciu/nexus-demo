import streamlit as st
import pandas as pd
import plotly.express as px
import math

def force_inject_mock_data():
    """Simulează baza de date pentru demo. Va fi înlocuită cu SQLite ulterior."""
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
    st.title(" NEXUS Manager Analytics")

    # === FILTRE GLOBALE ===
    col_f1, col_f2 = st.columns(2)
    with col_f1: analiza_client = st.selectbox("🎯 Client / Filială:", ["TOȚI CLIENȚII"] + clients_mock)
    with col_f2: analiza_produs = st.selectbox("📦 Produs:", list(st.session_state.db.keys()))
    st.divider()

    df_toate = st.session_state.db[analiza_produs]["livrari_totale"]
    if analiza_client != "TOȚI CLIENȚII":
        df_toate = df_toate[df_toate["Client"] == analiza_client]

    df_toate["Data_Obj"] = pd.to_datetime(df_toate["Data"], format="%d-%m-%Y")
    df_toate["Luna"] = df_toate["Data_Obj"].dt.to_period("M").dt.to_timestamp().dt.strftime("%b %Y")

    # === RAPORT 1: Vânzări pe 12 Luni ===
    st.markdown("#### 📈 1. Volum Livrări – Ultimele 12 Luni")
    df_luni = df_toate.groupby(["Luna", "Status_Plata"])["Volum_Paleti"].sum().reset_index()
    
    fig_luni = px.bar(df_luni, x="Luna", y="Volum_Paleti", color="Status_Plata",
                      color_discrete_map={"Achitat": "#28a745", "În termen": "#17a2b8", "Restanță": "#dc3545"},
                      hover_data={"Volum_Paleti": ":.0f paleți", "Luna": False, "Status_Plata": False},
                      title=f"{analiza_produs} → {analiza_client}")
    fig_luni.update_layout(xaxis_tickangle=-45, bargap=0.2, height=400, hovermode="x")
    st.plotly_chart(fig_luni, use_container_width=True)

    st.divider()

    # === RAPORT 2: Distribuție per Client ===
    st.markdown("#### 🏆 2. Distribuție Vânzări per Client")
    df_clienti = df_toate.groupby("Client")["Volum_Paleti"].sum().reset_index().sort_values("Volum_Paleti", ascending=False)
    
    fig_clienti = px.bar(df_clienti, x="Client", y="Volum_Paleti", color="Volum_Paleti",
                         color_continuous_scale="Blues",
                         hover_data={"Volum_Paleti": ":.0f paleți", "Client": False})
    fig_clienti.update_layout(xaxis_tickangle=-45, bargap=0.3, height=350, hovermode="x", coloraxis_showscale=False)
    st.plotly_chart(fig_clienti, use_container_width=True)

    st.divider()

    # === RAPORT 3: Status Stocuri (WMS) ===
    st.markdown("#### 📦 3. Status Stocuri (WMS)")
    p = st.session_state.db[analiza_produs]
    total_cutii = (p["stock_pal"] * p["conversion"]) + p["stock_box"]
    
    if total_cutii >= p["conversion"] * 2:
        status, msg = "🟢 OK", "Stoc suficient pentru ≥2 paleți"
    elif total_cutii >= p["conversion"] * 0.3:
        status, msg = "🟡 Mediu", f"Stoc pentru ~1 palet ({total_cutii:.0f} cutii)"
    else:
        status, msg = "🔴 Critic", f"Stoc sub prag ({total_cutii:.0f} cutii)"

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Paleți", p["stock_pal"])
    col_s2.metric("Cutii libere", p["stock_box"])
    col_s3.metric("Status", status, delta=msg, delta_color="inverse")
    
    st.progress(min(total_cutii / (p["conversion"] * 3), 1.0))
    st.caption(f"📊 Capacitate stoc: {total_cutii:.0f} / {p['conversion']*3:.0f} cutii (3 paleți = 100%)")

    # === LIVE FEED (opțional) ===
    with st.expander("🔴 LIVE: Comenzi recente"):
        if st.session_state.istoric_comenzi_live:
            st.dataframe(pd.DataFrame(st.session_state.istoric_comenzi_live).tail(5), hide_index=True, use_container_width=True)
        else:
            st.info("Nicio comandă nouă astăzi.")
