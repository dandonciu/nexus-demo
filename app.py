import streamlit as st
import time
from datetime import datetime
import math
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NEXUS B2B", page_icon="📦", layout="wide")

# --- BANNER / ANTET PRINCIPAL NEXUS ---
st.markdown("""
    <div style="background: linear-gradient(90deg, #003366 0%, #004080 100%); 
                padding: 20px 30px; 
                border-radius: 10px; 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                color: white; 
                margin-bottom: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div>
            <h1 style="margin: 0; padding: 0; color: #ffffff; font-size: 2.5rem; letter-spacing: 1px;">
                📦 NEXUS
            </h1>
            <p style="margin: 0; padding: 0; font-style: italic; color: #a8c5e8; font-size: 1.1rem; margin-top: -5px;">
                Rezolvă problemele, nu le creează.
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; padding: 0; font-weight: bold; font-size: 1.3rem; letter-spacing: 0.5px;">
                CORPORAȚIA ALPHA SRL
            </p>
            <p style="margin: 0; padding: 0; font-size: 0.95rem; color: #d0e1f9;">
                Sistem Integrat de Gestiune Operativă
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

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

if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

if 'schita_comanda' not in st.session_state:
    st.session_state.schita_comanda = []
    
if 'mod_previzualizare' not in st.session_state:
    st.session_state.mod_previzualizare = False

if 'istoric_comenzi_live' not in st.session_state:
    st.session_state.istoric_comenzi_live = []

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

def get_available_stock_ui(prod_key):
    total_db = get_total_boxes(prod_key)
    in_cart = sum([(item['Paleti'] * st.session_state.db[prod_key]['conversion']) + item['Cutii'] 
                   for item in st.session_state.schita_comanda if item['Produs'] == prod_key])
    rem = total_db - in_cart
    conv = st.session_state.db[prod_key]['conversion']
    return rem // conv, rem % conv

def calculate_delta(prod_key, cmd_pal, cmd_box):
    total_stock = get_total_boxes(prod_key)
    in_cart = sum([(item['Paleti'] * st.session_state.db[prod_key]['conversion']) + item['Cutii'] 
                   for item in st.session_state.schita_comanda if item['Produs'] == prod_key])
    p = st.session_state.db[prod_key]
    total_cmd = (cmd_pal * p['conversion']) + cmd_box + in_cart
    
    if total_cmd > total_stock: return None
    return True

# --- ECRAN LOGIN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("💡 Cine sunteți: 'angajat' sau 'manager'")
        with st.form("login_form"):
            pwd = st.text_input("Parolă", type="password")
            if st.form_submit_button("Log In (Enter)"):
                if pwd in ["angajat", "manager"]:
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
        
    tab1, tab2, tab3 = st.tabs(["🛒 Lansare Comandă", "🚚 Status & Documente", "📥 Recepție Marfă"])
    
    # ==========================================
    # TAB 1: LANSARE COMANDĂ (Coș / Schiță)
    # ==========================================
    with tab1:
        client_ales = st.selectbox("1. Selectează Beneficiarul:", clients_mock)
        
        # --- ECRAN A: ADĂUGARE ÎN SCHIȚĂ ---
        if not st.session_state.mod_previzualizare:
            st.markdown("### 📋 Formare Schiță Comandă")
            
            with st.container():
                prod_name = st.selectbox("Alege Produsul:", list(st.session_state.db.keys()), on_change=force_reset)
                p_data = st.session_state.db[prod_name]
                
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
                            <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod dB Depozit (Palet)</div>
                            <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['oracle_pal']}</div>
                        </div>
                        <div style='flex: 1; min-width: 150px; margin-bottom: 10px;'>
                            <div style='font-size: 0.85rem; color: #555; margin-bottom: 2px;'>Cod dB Depozit (Cutie)</div>
                            <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['oracle_box']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                av_pal, av_box = get_available_stock_ui(prod_name)
                
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("📦 Stoc PALEȚI Disponibil", av_pal)
                col_s2.metric("📦 Stoc CUTII libere Disp.", av_box)
                col_s3.metric("🔄 Cutii per Palet", f"{p_data['conversion']} buc")
                
                col_q1, col_q2 = st.columns(2)
                with col_q1: order_pal = st.number_input("Nr. PALEȚI comandați:", min_value=0, step=1, key=f'input_pal_{st.session_state.reset_counter}')
                with col_q2: order_box = st.number_input("Nr. CUTII comandate:", min_value=0, step=1, key=f'input_box_{st.session_state.reset_counter}')
                
                if st.button("➕ Adaugă în Listă"):
                    if order_pal == 0 and order_box == 0:
                        st.warning("Introduceți o cantitate înainte de a adăuga.")
                    else:
                        is_valid = calculate_delta(prod_name, order_pal, order_box)
                        if not is_valid:
                            st.error("❌ STOC INSUFICIENT pentru această cantitate!")
                        else:
                            st.session_state.schita_comanda.append({
                                "Produs": prod_name,
                                "Paleti": order_pal,
                                "Cutii": order_box,
                                "Cod_Depozit_Pal": p_data['oracle_pal'],
                                "Cod_Depozit_Box": p_data['oracle_box']
                            })
                            st.success(f"Adăugat: {prod_name} ({order_pal} Pal, {order_box} Cutii)")
                            force_reset()
                            st.rerun()

            st.divider()

            if len(st.session_state.schita_comanda) > 0:
                st.markdown(f"#### 🛒 Produse în comanda curentă (Către: {client_ales})")
                
                df_schita = pd.DataFrame(st.session_state.schita_comanda)[['Produs', 'Paleti', 'Cutii']]
                df_schita['Paleti'] = df_schita['Paleti'].astype(str)
                df_schita['Cutii'] = df_schita['Cutii'].astype(str)
                
                st.dataframe(df_schita, use_container_width=True, hide_index=True)
                
                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    if st.button("🗑️ Golește Lista"):
                        st.session_state.schita_comanda = []
                        st.rerun()
                with col_btn2:
                    if st.button("👁️ Previzualizare & Finalizare", type="primary", use_container_width=True):
                        st.session_state.mod_previzualizare = True
                        st.rerun()
            else:
                st.info("Schița este goală. Adăugați produse pentru a forma o comandă.")

        # --- ECRAN B: PREVIZUALIZARE & TRIMITERE ---
        else:
            st.markdown("### 🔍 Previzualizare Aviz (Înainte de Trimitere)")
            
            st.markdown(f"""
            <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #fff;'>
                <h4 style='text-align: center; color: #003366;'>PROIECT AVIZ EXPEDIȚIE - NEXUS</h4>
                <p><b>Data:</b> {data_azi}<br>
                <b>Client Beneficiar:</b> {client_ales}<br>
                <b>Nr. Comandă Interne:</b> CMD-{st.session_state.order_number}</p>
                <hr>
            </div>
            """, unsafe_allow_html=True)
            
            df_previzualizare = pd.DataFrame(st.session_state.schita_comanda)[['Produs', 'Paleti', 'Cutii']]
            df_previzualizare['Paleti'] = df_previzualizare['Paleti'].astype(str)
            df_previzualizare['Cutii'] = df_previzualizare['Cutii'].astype(str)
            st.table(df_previzualizare)
            
            st.warning("⚠️ Vă rugăm să verificați cantitățile. Odată lansată, comanda blochează stocul și ajunge pe tableta operatorilor din depozit.")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔙 Întoarce-te (Mai adaugă produse)"):
                    st.session_state.mod_previzualizare = False
                    st.rerun()
            with col_b2:
                if st.button("🚀 CONFIRMĂ ȘI LANSEAZĂ SPRE dB DEPOZIT", type="primary", use_container_width=True):
                    
                    totaluri_cos = {}
                    for item in st.session_state.schita_comanda:
                        prod = item['Produs']
                        cutii_total_item = (item['Paleti'] * st.session_state.db[prod]['conversion']) + item['Cutii']
                        totaluri_cos[prod] = totaluri_cos.get(prod, 0) + cutii_total_item
                        
                    for prod, cutii_de_scazut in totaluri_cos.items():
                        stoc_curent = get_total_boxes(prod)
                        stoc_ramas = stoc_curent - cutii_de_scazut
                        conv = st.session_state.db[prod]['conversion']
                        
                        st.session_state.db[prod]['stock_pal'] = stoc_ramas // conv
                        st.session_state.db[prod]['stock_box'] = stoc_ramas % conv
                    
                    st.session_state.db = st.session_state.db

                    st.session_state.istoric_comenzi_live.append({
                        "Comanda": f"CMD-{st.session_state.order_number}",
                        "Client": client_ales,
                        "Articole": len(st.session_state.schita_comanda),
                        "Status": "Așteaptă Încărcare",
                        "Data_Ora": datetime.now().strftime("%H:%M:%S")
                    })

                    st.success(f"✅ Comanda CMD-{st.session_state.order_number} a fost trimisă spre dB Depozit!")
                    
                    st.session_state.order_number += 1
                    st.session_state.schita_comanda = []
                    st.session_state.mod_previzualizare = False
                    time.sleep(1.5)
                    st.rerun()

    # ==========================================
    # TAB 2: STATUS & DOCUMENTE
    # ==========================================
    with tab2:
        st.markdown("### 🚚 Confirmare Depozit & Emitere Documente")
        
        comenzi_lansate = st.session_state.istoric_comenzi_live
        
        if len(comenzi_lansate) == 0:
            st.info("Nicio comandă nu a fost lansată încă spre depozit.")
        else:
            for idx, cmd in enumerate(comenzi_lansate):
                cu_status_incarcat = cmd.get('status_incarcat', False)
                border_color = "#28a745" if cu_status_incarcat else "#ffc107"
                bg_color = "#f9fff9" if cu_status_incarcat else "#fffdf5"
                
                st.markdown(f"""
                <div style='border-left: 5px solid {border_color}; background-color: {bg_color}; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                    <h4 style='margin-top: 0; color: #003366;'>{cmd['Comanda']} - {cmd['Client']}</h4>
                    <p style='margin-bottom: 0;'><b>Articole:</b> {cmd['Articole']} | <b>Ora lansării:</b> {cmd['Data_Ora']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn_a, col_btn_b, col_btn_c = st.columns([1, 2, 2])
                
                with col_btn_a:
                    if not cu_status_incarcat:
                        if st.button("📲 Simulare: Confirmat Depozit", key=f"sim_dep_{idx}"):
                            st.session_state.istoric_comenzi_live[idx]['Status'] = "Încărcat. Gata de printare."
                            st.session_state.istoric_comenzi_live[idx]['status_incarcat'] = True
                            st.rerun()
                    else:
                        st.success("✅ Marfă Încărcată")

                with col_btn_b:
                    if cu_status_incarcat:
                        daca_emis = cmd.get('document_emis', False)
                        if not daca_emis:
                            if st.button("🖨️ EMITE AVIZUL (Și trimite la SmartBill și Depozit)", type="primary", key=f"emit_{idx}"):
                                st.session_state.istoric_comenzi_live[idx]['document_emis'] = True
                                st.session_state.istoric_comenzi_live[idx]['Status'] = "Finalizat"
                                
                                st.success("✅ Aviz și Decl. Conf. Emise. Documente finalizate trimise la SmartBill și la Depozit.")
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.info("Documente finalizate.")
                st.divider()

    # ==========================================
    # TAB 3: RECEPȚIE
    # ==========================================
    with tab3:
        st.markdown("### 📥 Sincronizare Recepții (Așteptare SmartBill)")
        st.info("🚧 În producție, acest ecran va fi populat automat cu NIR-urile noi emise de SmartBill.")


# ==========================================
# --- APLICAȚIA MANAGER ---
# ==========================================
elif st.session_state.role == "manager":
    
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
        
        with st.expander("📝 Vezi descriere produs & Date dB Depozit"):
            st.write(f"**Descriere Nomenclator:** {p_val['descriere']}")
            st.write("Aici vom putea importa și alte câmpuri din dB Depozit: Lot, Data Expirării, Locație raft depozit, etc.")

        if p_val['stock_box'] > (p_val['conversion'] * 0.7):
            st.error(f"🔴 ATENȚIE: Aveți prea multe cutii libere ({p_val['stock_box']}).")
        elif p_val['stock_box'] > 0:
            st.warning("🟠 INFO: Există cutii libere în depozit.")
        else:
            st.success("🟢 OPTIM: Nu aveți fracții desfăcute în depozit.")
            
        st.divider()
        st.subheader("3. Rapoarte Operative Rapide")
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
        with col_m3: raport = st.selectbox("Meniu Delirant 🤣", ["Evoluție Volume & Plăți", "Raportări dB Depozit"])
        
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
            
        elif raport == "Raportări dB Depozit":
            st.info("🔄 Se afișează rapoartele sincronizate din baza de date a depozitului.")
            st.dataframe(pd.DataFrame({
                "Nume Raport": ["Balanță Stocuri", "Rotație Marfă", "Facturi Emise vs Încasate"],
                "Ultima Actualizare": ["Azi 08:00", "Ieri 18:00", "Azi 09:15"],
                "Status Sincronizare": ["OK", "OK", "Pending"]
            }), hide_index=True)
