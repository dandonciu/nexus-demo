import streamlit as st
import pandas as pd
import plotly.express as px

def force_inject_mock_data():
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

    tab_op, tab_an = st.tabs(["⚡ A. Situație Operațională", "📊 B. Privire de Ansamblu (Analiză)"])

    with tab_op:
        st.subheader("🔴 LIVE FEED: Comenzi Noi")
        if st.session_state.istoric_comenzi_live:
            st.dataframe(pd.DataFrame(st.session_state.istoric_comenzi_live).tail(5), hide_index=True, use_container_width=True)
        else:
            st.info("Nicio comandă nouă lansată astăzi.")
        st.divider()
        st.subheader("📦 Status Stoc Punctual (WMS)")
        mgr_prod = st.selectbox("Selectare Produs:", list(st.session_state.db.keys()))
        p_val = st.session_state.db[mgr_prod]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Paleți Intacți", p_val['stock_pal'])
        c2.metric("Cutii Libere", p_val['stock_box'])
        c3.metric("Conversie WMS", f"{p_val['conversion']} cutii/palet")
        total_boxes = (p_val['stock_pal'] * p_val['conversion']) + p_val['stock_box']
        c4.metric("Total Disponibil (Cutii)", total_boxes)
        if p_val['stock_box'] > (p_val['conversion'] * 0.7):
            st.error(f"🔴 ATENȚIE: Prea multe cutii libere ({p_val['stock_box']}). Recomandare: Împachetează.")
        elif p_val['stock_box'] > 0:
            st.warning("🟠 INFO: Există fracțiuni desfăcute.")
        else:
            st.success("🟢 OPTIM: Stoc compact.")

    with tab_an:
        col_f1, col_f2 = st.columns(2)
        with col_f1: analiza_client = st.selectbox(" Client / Filială:", ["TOȚI CLIENȚII"] + clients_mock)
        with col_f2: analiza_produs = st.selectbox("📦 Produs:", list(st.session_state.db.keys()), key="mgr_prod_an")
        st.divider()

        df_toate = st.session_state.db[analiza_produs]["livrari_totale"]
        if analiza_client != "TOȚI CLIENȚII":
            df_toate = df_toate[df_toate["Client"] == analiza_client]

        df_toate["Data_Obj"] = pd.to_datetime(df_toate["Data"], format="%d-%m-%Y")
        df_toate["Luna"] = df_toate["Data_Obj"].dt.to_period("M").dt.to_timestamp().dt.strftime("%b %Y")

        st.markdown("#### 📆 1. Volum Livrări – Ultimele 12 Luni")
        df_luni = df_toate.groupby(["Luna", "Status_Plata"])["Volum_Paleti"].sum().reset_index()
        fig_luni = px.bar(df_luni, x="Luna", y="Volum_Paleti", color="Status_Plata",
                          color_discrete_map={"Achitat": "#28a745", "În termen": "#17a2b8", "Restanță": "#dc3545"})
        fig_luni.update_layout(hovermode='closest', xaxis_tickangle=-45, bargap=0.15, height=400)
        fig_luni.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<extra></extra>",
                               hoverlabel=dict(bgcolor="#1E1E2E", font_color="white", bordercolor="#00ADB5"))
        st.plotly_chart(fig_luni, use_container_width=True)

        st.divider()

        st.markdown("####  2. Distribuție Volum per Client")
        df_top = df_toate.groupby("Client")["Volum_Paleti"].sum().reset_index().sort_values("Volum_Paleti", ascending=False)
        fig_top = px.bar(df_top, x="Client", y="Volum_Paleti", color_discrete_sequence=["#00ADB5"])
        fig_top.update_layout(hovermode='closest', xaxis_tickangle=-45, bargap=0.3, height=350)
        fig_top.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<extra></extra>",
                              hoverlabel=dict(bgcolor="#1E1E2E", font_color="white", bordercolor="#00ADB5"),
                              marker_line_color='white', marker_line_width=1.5)
        st.plotly_chart(fig_top, use_container_width=True)

        st.divider()

        st.markdown("#### 🔎 3. Istoric Zilnic (Detaliu)")
        if analiza_client == "TOȚI CLIENȚII":
            st.info("💡 Pentru detalii zilnice, selectează un anumit client din filtrul de sus.")
        elif df_toate.empty:
            st.warning("Nu există date pentru selecția curentă.")
        else:
            fig_detaliu = px.bar(df_toate, x="Data", y="Volum_Paleti", color="Status_Plata",
                                 color_discrete_map={"Achitat": "#28a745", "În termen": "#17a2b8", "Restanță": "#dc3545"})
            fig_detaliu.update_layout(hovermode='closest', xaxis_tickangle=-45, bargap=0.3, height=400)
            fig_detaliu.update_traces(hovertemplate="<b>%{y:.0f}</b> paleți<br>%{x}<extra></extra>",
                                      hoverlabel=dict(bgcolor="#1E1E2E", font_color="white", bordercolor="#00ADB5"))
            st.plotly_chart(fig_detaliu, use_container_width=True)
