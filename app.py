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
                    " ├─ Filiala Cluj", " ├─ Filiala Cluj", " ├─ Filiala Cluj", " ├─ Filiala Cluj",
                    "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION"
                ],
                "Data": [
                    "10-01-2024", "15-02-2024", "05-03-2024", "10-04-2024", "28-04-2024",
                    "12-01-2024", "18-02-2024", "15-03-2024", "20-04-2024",
                    "05-01-2024", "20-02-2024", "10-03-2024", "15-04-2024",
                    "08-01-2024", "14-02-2024", "02-03-2024", "22-04-2024", "05-05-2024"
                ],
                "Volum_Paleti": [12, 15, 22, 14, 8,   5, 8, 4, 6,   4, 6, 8, 4,   20, 18, 25, 12, 15],
                "Status_Plata": [
                    "Achitat", "Achitat", "Restanță", "În termen", "În termen",
                    "Achitat", "Achitat", "Achitat", "În termen",
                    "Achitat", "Achitat", "Restanță", "În termen",
                    "Achitat", "Achitat", "Restanță", "În termen", "În termen"
                ]
            })
        },
        "Lavete Craft Puromore Blue": {
            "cod_master": "MST-70117",  "cod_nir": "NIR-8820",
            "oracle_pal": "PAL 70117", "oracle_box": "70117",
            "stock_pal": 1, "stock_box": 10, "conversion": 120,
            "descriere": "Lavete industriale rezistente la solvenți, culoare albastră, 500 porții/rolă. Greutate palet: 180kg.",
            "livrari_totale": pd.DataFrame({
                "Client": [
                    "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL",
                    " ├─ Filiala București Nord", " ├─ Filiala București Nord", " ├─ Filiala București Nord", " ├─ Filiala București Nord",
                    " ├─ Filiala Cluj", " ├─ Filiala Cluj", " ├─ Filiala Cluj", " ├─ Filiala Cluj",
                    "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION"
                ],
                "Data": [
                    "05-01-2024", "12-02-2024", "01-03-2024", "15-04-2024",
                    "20-01-2024", "25-02-2024", "10-03-2024", "05-04-2024",
                    "15-01-2024", "28-02-2024", "15-03-2024", "20-04-2024",
                    "10-01-2024", "20-02-2024", "05-03-2024", "15-04-2024", "02-05-2024"
                ],
                "Volum_Paleti": [5, 8, 12, 10,   2, 4, 3, 5,   8, 6, 4, 5,   15, 20, 18, 22, 10],
                "Status_Plata": [
                    "Achitat", "Achitat", "Restanță", "În termen",
                    "Achitat", "Achitat", "Achitat", "În termen",
                    "Achitat", "Achitat", "Restanță", "În termen",
                    "Achitat", "Achitat", "Restanță", "În termen", "În termen"
                ]
            })
        }
    }

clients_mock = [
    "🏢 [HQ] SC CORPORATIA ALPHA SRL", 
    " ├─ Filiala București Nord", 
    " ├─ Filiala Cluj", 
    "🏢 [HQ] BETA DISTRIBUTION"
]

def get_total_boxes(prod_key):
    p = st.session_state.db[prod_key]
    return (p['stock_pal'] * p['conversion']) + p['stock_box']

def calculate_delta(prod_key, cmd_pal, cmd_box):
    p = st.session_state.db[prod_key]
    total_stock = get_total_boxes(prod_key)
    total_cmd = (cmd_pal * p['conversion']) + cmd_box
    if total_cmd > total_stock: return None
    rem = total_stock - total_cmd
    return (rem // p['conversion'], rem % p['conversion'])

# --- ECRAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 NEXUS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("💡 Cine sunteți: 'angajat' sau 'manager'")
        with st.form("login_form"):
            pwd = st.text_input("Parolă", type="password")
            if st.form_submit_button("Log In (Enter)"):
                if pwd in ["angajat-no", "manager-no"]:
                    st.session_state.logged_in = True
                    st.session_state.role = pwd
                    st.rerun()
                else: st.error("Parolă incorectă!")
    st.stop()

col_logo, col_logout = st.columns([8, 1])
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.logged_in, st.session_state.role = False, None
        st.rerun()

# ==========================================
# --- APLICAȚIA ANGAJAT ---
# ==========================================
if st.session_state.role == "angajat":
    
    col_titlu, col_cmd = st.columns([4, 1])
    with col_titlu:
        st.title("⚡ NEXUS Operațional")
    with col_cmd:
        data_azi = datetime.now().strftime("%d.%m.%Y")
        st.info(f"**Nr. Cmd:** {st.session_state.order_number}  \n**Data:** {data_azi}")
        
    tab1, tab2 = st.tabs(["🛒 Lansare Comandă", "📥 Recepție Marfă"])
    
    with tab1:
        client = st.selectbox("1. Selectează Beneficiarul:", clients_mock)
        
        # Legăm force_reset de dropdown
        prod_name = st.selectbox("2. Selectează Produsul:", list(st.session_state.db.keys()), on_change=force_reset)
        p_data = st.session_state.db[prod_name]
        
        st.markdown(f"#### 📦 {prod_name}")
        
# Afișare modernă coduri (pe un singur rând, adaptabil pe telefon)
        st.markdown(f"""
        <div style='background-color: #f0f7f4; padding: 20px; border-radius: 8px; border-left: 5px solid #28a745; margin-bottom: 20px;'>
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>
                <div style='flex: 1; min-width: 180px; margin-bottom: 10px;'>
                    <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod produs (NEXUS)</div>
                    <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['cod_master']}</div>
                </div>
                <div style='flex: 1; min-width: 150px; margin-bottom: 10px;'>
                    <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod NIR</div>
                    <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['cod_nir']}</div>
                </div>
                <div style='flex: 1; min-width: 200px; margin-bottom: 10px;'>
                    <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod Depozit (palet întreg)</div>
                    <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['oracle_pal']}</div>
                </div>
                <div style='flex: 1; min-width: 150px; margin-bottom: 10px;'>
                    <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod Depozit (Cutie)</div>
                    <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['oracle_box']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("👇 **1. STOC ACTUAL**")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("📦 Stoc PALEȚI", p_data['stock_pal'])
        col_s2.metric("📦 Stoc CUTII libere", p_data['stock_box'])
        col_s3.metric("🔄 Cutii per Palet", f"{p_data['conversion']} buc")
        
        st.divider()
        st.markdown("👇 **2. INTRODUCEȚI COMANDA**")
        col_q1, col_q2 = st.columns(2)
        
        # Legăm widgeturile de reset_counter. Astfel, când se schimbă counter-ul, revin automat la 0
        with col_q1: order_pal = st.number_input("Nr. PALEȚI comandați:", min_value=0, step=1, key=f'input_pal_{st.session_state.reset_counter}')
        with col_q2: order_box = st.number_input("Nr. CUTII comandate:", min_value=0, step=1, key=f'input_box_{st.session_state.reset_counter}')
        
        if order_pal > 0 or order_box > 0:
            delta = calculate_delta(prod_name, order_pal, order_box)
            if delta is None: st.error("❌ STOC INSUFICIENT!")
            else:
                rem_pal, rem_box = delta
                st.divider()
                st.success("👇 **3. STOC RĂMAS (După Validare)**")
                c1, c2 = st.columns(2)
                c1.metric("Paleți Rămași:", rem_pal)
                c2.metric("Cutii Rămase:", rem_box)
                
                if st.button("🚀 Trimite Comanda spre Oracle & SmartBill", type="primary"):
                    cmd_salvata = st.session_state.order_number
                    
                    # Update Stoc
                    st.session_state.db[prod_name]['stock_pal'] = rem_pal
                    st.session_state.db[prod_name]['stock_box'] = rem_box
                    
                    st.success(f"✅ Comanda {cmd_salvata} a fost procesată cu succes!")
                    
                    # Incrementăm comanda și forțăm widgeturile la 0 pentru noua comandă
                    st.session_state.order_number += 1
                    force_reset()
                    
                    st.code(f"""
--- STATUS COMANDĂ: {cmd_salvata} ---
Beneficiar: {client}
Comandă lansată pentru: 
  -> {order_pal} x {p_data['oracle_pal']}
  -> {order_box} x {p_data['oracle_box']}

[RĂSPUNS AȘTEPTAT DE LA ORACLE (WebHook)]
Status: PENDING DEPOT...
(Câmpurile "Avizat la data de...", "Nr. Auto" și "Nume Șofer" 
 se vor completa automat în NEXUS DB când Oracle închide avizul de expediție.)

[URMĂTORUL PAS AUTOMAT]
La recepția avizului din Oracle -> NEXUS trimite Date Facturare la SmartBill.
                    """, language="log")

    with tab2:
        st.markdown("### 📥 Sincronizare Recepții (Așteptare SmartBill)")
        st.info("🚧 În producție, acest ecran va fi populat automat cu NIR-urile noi emise de SmartBill. Angajatul doar va confirma recepția fizică a mărfii.")

# ==========================================
# --- APLICAȚIA MANAGER ---
# ==========================================
elif st.session_state.role == "manager":
    st.title("📈 NEXUS Dashboard Manager")
    
    tab_op, tab_an = st.tabs(["⚡ A. Situație Operativă (Birou)", "📊 B. Analiză Generală (Ședințe)"])
    
    with tab_op:
        st.subheader("1. Privire de Ansamblu")
        c_k1, c_k2, c_k3 = st.columns(3)
        c_k1.success("Livrări în grafic (Azi): 4")
        c_k2.warning("Recepții în așteptare (SmartBill): 1")
        c_k3.error("Facturi restante clienți: 2")
        
        st.divider()
        st.subheader("2. Analiză Stoc Punctual")
        mgr_prod = st.selectbox("Selectare Produs:", list(st.session_state.db.keys()))
        p_val = st.session_state.db[mgr_prod]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Paleți Intacți", p_val['stock_pal'])
        c2.metric("Cutii Libere", p_val['stock_box'])
        c3.metric("Conversie", f"{p_val['conversion']} cutii/palet")
        
        billed = math.ceil(get_total_boxes(mgr_prod) / p_val['conversion'])
        c4.metric("Facturare Depozit", f"{billed} paleți")
        
        with st.expander("📝 Vezi descriere produs & Date Oracle"):
            st.write(f"**Descriere Nomenclator:** {p_val['descriere']}")
            st.write("Aici vom putea importa și alte câmpuri din Oracle: Lot, Data Expirării, Locație raft depozit, etc.")

        if p_val['stock_box'] > (p_val['conversion'] * 0.7):
            st.error(f"🔴 ATENȚIE: Aveți prea multe cutii libere ({p_val['stock_box']}).")
        elif p_val['stock_box'] > 0:
            st.warning("🟠 INFO: Există cutii libere în depozit.")
        else:
            st.success("🟢 OPTIM: Nu aveți fracții desfăcute în depozit.")
            
        st.divider()
        st.subheader("3. Rapoarte Operative Rapide (Oracle)")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            with st.expander("🚨 Mărfuri sub stoc critic"):
                st.dataframe(pd.DataFrame({
                    "Produs": ["Săpun Lichid 5L", "Role Prosop Z"],
                    "Stoc Curent": ["0 Pal", "1 Pal"],
                    "Necesar Minim": ["5 Pal", "10 Pal"]
                }), hide_index=True)
        with col_r2:
            with st.expander("🚚 Livrări Programate Azi"):
                st.dataframe(pd.DataFrame({
                    "Client": ["BETA DISTRIBUTION", "Filiala Cluj"],
                    "Status": ["Se încarcă", "Așteaptă auto"],
                    "Ora": ["14:00", "16:30"]
                }), hide_index=True)
                
    with tab_an:
        col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
        with col_m1: analiza_client = st.selectbox("Selectează Client / Filială:", clients_mock)
        with col_m2: analiza_produs = st.selectbox("Selectează Produs:", list(st.session_state.db.keys()), key="mgr_prod_an")
        with col_m3: raport = st.selectbox("Meniu Delirant 🤣", ["Evoluție Volume & Plăți", "Raportări Oracle"])
        
        if raport == "Evoluție Volume & Plăți":
            st.markdown(f"#### 📊 Istoric Livrări: **{analiza_produs}** către **{analiza_client}**")
            
            df_toate = st.session_state.db[analiza_produs]["livrari_totale"]
            df_filtrat = df_toate[df_toate['Client'] == analiza_client]
            
            if df_filtrat.empty:
                st.warning(f"Nu există date de livrare pentru {analiza_produs} către {analiza_client}.")
            else:
                color_discrete_map = {'Achitat': '#28a745', 'În termen': '#17a2b8', 'Restanță': '#dc3545'}
                
                fig = px.bar(
                    df_filtrat, x='Data', y='Volum_Paleti', color='Status_Plata',
                    text='Volum_Paleti', color_discrete_map=color_discrete_map,
                    title="Volum Paleți / Dată Exactă"
                )
                fig.update_traces(textposition='outside', width=0.4)
                fig.update_layout(xaxis_type='category')
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 💸 Detalii Tranzacții")
                def color_status(val): return 'color: #28a745; font-weight:bold;' if val == 'Achitat' else 'color: #dc3545; font-weight:bold;' if 'Restanță' in str(val) else 'color: #17a2b8;'
                st.dataframe(df_filtrat[['Data', 'Volum_Paleti', 'Status_Plata']].style.map(color_status, subset=['Status_Plata']), hide_index=True)
            
        elif raport == "Raportări Oracle":
            st.info("🔄 Se afișează rapoartele sincronizate din vechiul sistem Oracle.")
            st.dataframe(pd.DataFrame({
                "Nume Raport": ["Balanță Stocuri", "Rotație Marfă", "Facturi Emise vs Încasate"],
                "Ultima Actualizare": ["Azi 08:00", "Ieri 18:00", "Azi 09:15"],
                "Status Sincronizare": ["OK", "OK", "Pending"]
            }), hide_index=True)
