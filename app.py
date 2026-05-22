import streamlit as st
import time
from datetime import datetime
import math
import pandas as pd
import plotly.express as px
import pytz

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
                Sistem Auto-Convertor: Logistic-Fiscal
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; padding: 0; font-weight: bold; font-size: 1.3rem; letter-spacing: 0.5px;">
                NOVA SAFE SRL
            </p>
            <p style="margin: 0; padding: 0; font-size: 0.95rem; color: #d0e1f9;">
                Sistem Integrat de Gestiune Operativă
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CSS PENTRU EVIDENȚIEREA PAȘILOR DE SELECȚIE ---
st.markdown("""
    <style>
    .stSelectbox label { font-size: 1.1rem !important; font-weight: bold !important; color: #003366 !important; }
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
elif len(st.session_state.schita_comanda) > 0 and 'Paleti' not in st.session_state.schita_comanda[0]:
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
            "stock_pal": 3, "stock_box": 10, "conversion": 64,
            "um_baza": "Role", "conversie_baza": 6,             
            "descriere": "Role din celuloză pură 100%, 2 straturi, destinate dispenserelor auto-cut.",
            "livrari_totale": pd.DataFrame({
                "Client": [
                    "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", " ├─ Filiala București Nord", " ├─ Filiala Cluj", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION"
                ],
                "Data": ["10-01-2024", "15-02-2024", "12-01-2024", "05-01-2024", "08-01-2024", "14-02-2024"],
                "Volum_Paleti": [12, 15, 5, 4, 20, 18],
                "Status_Plata": ["Achitat", "Achitat", "Achitat", "Achitat", "Achitat", "Achitat"]
            })
        },
        "Lavete Craft Puromore Blue": {
            "cod_master": "MST-70117",  "cod_nir": "NIR-8820",
            "oracle_pal": "PAL 70117", "oracle_box": "70117",
            "stock_pal": 2, "stock_box": 50, "conversion": 120, 
            "um_baza": "Lavete", "conversie_baza": 14,          
            "descriere": "Lavete industriale rezistente la solvenți, culoare albastră, 500 porții/rolă.",
            "livrari_totale": pd.DataFrame({
                "Client": [
                    "🏢 [HQ] SC CORPORATIA ALPHA SRL", "🏢 [HQ] SC CORPORATIA ALPHA SRL", " ├─ Filiala București Nord", " ├─ Filiala Cluj", "🏢 [HQ] BETA DISTRIBUTION", "🏢 [HQ] BETA DISTRIBUTION"
                ],
                "Data": ["05-01-2024", "12-02-2024", "20-01-2024", "15-01-2024", "10-01-2024", "20-02-2024"],
                "Volum_Paleti": [5, 8, 2, 8, 15, 20],
                "Status_Plata": ["Achitat", "Achitat", "Achitat", "Achitat", "Achitat", "Restanță"]
            })
        }
    }

clients_mock = [
    "🏢 [HQ] SC CORPORATIA ALPHA SRL", 
    " ├─ Filiala București Nord", 
    " ├─ Filiala Cluj", 
    "🏢 [HQ] BETA DISTRIBUTION"
]

# --- ALIAS-URI DINAMICE MAPATE PE CLIENT ---
client_aliases = {
    "🏢 [HQ] SC CORPORATIA ALPHA SRL": {
        "Cârpe albastre": "Lavete Craft Puromore Blue"
    },
    " ├─ Filiala București Nord": {
        "Cârpe albastre": "Lavete Craft Puromore Blue",
        "Role ștergere Z": "Role Autocut Albe TAD 220m"
    },
    "🏢 [HQ] BETA DISTRIBUTION": {
        "Hârtie Mâini albă (General)": "Role Autocut Albe TAD 220m",
        "Cârpe franjurate": "Lavete Craft Puromore Blue"
    }
}

def get_total_boxes(prod_key):
    p = st.session_state.db[prod_key]
    return (p['stock_pal'] * p['conversion']) + p['stock_box']

def get_available_stock_ui(prod_key):
    total_db = get_total_boxes(prod_key)
    in_cart = sum([(item.get('Paleti', 0) * st.session_state.db[prod_key]['conversion']) + item.get('Cutii', 0) 
                   for item in st.session_state.schita_comanda if item.get('Produs') == prod_key])
    rem = total_db - in_cart
    conv = st.session_state.db[prod_key]['conversion']
    return rem // conv, rem % conv

def calculate_delta(prod_key, cmd_pal, cmd_box):
    total_stock = get_total_boxes(prod_key)
    in_cart = sum([(item.get('Paleti', 0) * st.session_state.db[prod_key]['conversion']) + item.get('Cutii', 0) 
                   for item in st.session_state.schita_comanda if item.get('Produs') == prod_key])
    p = st.session_state.db[prod_key]
    total_cmd = (cmd_pal * p['conversion']) + cmd_box + in_cart
    if total_cmd > total_stock: return False
    return True

# ==========================================
# --- ECRAN LOGIN ---
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 NEXUS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("💡 Autentificare (parole: 'angajat' sau 'manager')")
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
       data_azi = datetime.now(pytz.timezone('Europe/Bucharest')).strftime("%d.%m.%Y")
       st.info(f"**Nr. Cmd:** {st.session_state.order_number}  \n**Data:** {data_azi}")
        
    tab1, tab2, tab3 = st.tabs(["🛒 Lansare Comandă", "🚚 Status & Documente", "📥 Recepție Marfă"])
    
    # ==========================================
    # TAB 1: LANSARE COMANDĂ
    # ==========================================
    with tab1:
        comenzi_pending = [cmd for cmd in st.session_state.istoric_comenzi_live if cmd.get('status_incarcat', False) and not cmd.get('document_emis', False)]
        
        if len(comenzi_pending) > 0:
            ora_alertei = datetime.now(pytz.timezone('Europe/Bucharest')).strftime("%H:%M")
            st.markdown(f"""
            <div style='background-color: #fff3f3; border-left: 5px solid #dc3545; padding: 15px; margin-bottom: 20px; border-radius: 4px; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <div style='font-size: 2.2rem; margin-right: 15px;'>🚨</div>
                <div>
                    <h4 style='color: #dc3545; margin: 0;'>ACȚIUNE NECESARĂ ({ora_alertei}): {len(comenzi_pending)} mașină/mașini așteaptă actele la rampă!</h4>
                    <p style='margin: 0; font-size: 0.95rem; color: #555;'>Treceți în tab-ul <b>'Status & Documente'</b> pentru a emite Avizul și a elibera camionul.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if not st.session_state.mod_previzualizare:
            st.markdown("### 📋 Formare Schiță Comandă")
            st.divider()
            
            with st.container():
                
                st.markdown("<h4 style='color: #d9534f; margin-bottom: 5px;'>1. Selectează Beneficiarul:</h4>", unsafe_allow_html=True)
                client_ales = st.selectbox("Client", clients_mock, key="select_client", label_visibility="collapsed")
                
                baza_produse = list(st.session_state.db.keys())
                aliasuri_client_curent = client_aliases.get(client_ales, {})
                produse_disponibile = baza_produse + list(aliasuri_client_curent.keys())
                
                st.markdown("<h4 style='color: #d9534f; margin-top: 15px; margin-bottom: 5px;'>2. Alege Produsul (Căutare rapidă):</h4>", unsafe_allow_html=True)
                selected_option = st.selectbox("Produs", produse_disponibile, on_change=force_reset, key="select_prod", label_visibility="collapsed")
                
                if selected_option in aliasuri_client_curent:
                    prod_name = aliasuri_client_curent[selected_option]
                    alias_folosit = selected_option
                    st.success(f"🔄 Sistemul a recunoscut aliasul clientului: **{selected_option}** = **{prod_name}**")
                else:
                    prod_name = selected_option
                    alias_folosit = None

                p_data = st.session_state.db[prod_name]
                
                st.markdown(f"""
                <div style='background-color: #f0f7f4; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745; margin-top: 15px; margin-bottom: 20px;'>
                    <div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>
                        <div style='padding-right: 15px;'><span style='font-size: 0.85rem; color: #555;'>Cod NIR (Fiscal):</span> <br><span style='color: #28a745; font-size: 1.1rem; font-weight: bold;'>{p_data['cod_nir']}</span></div>
                        <div style='padding-right: 15px;'><span style='font-size: 0.85rem; color: #555;'>Cod dB (Palet):</span> <br><span style='color: #28a745; font-size: 1.1rem; font-weight: bold;'>{p_data['oracle_pal']}</span></div>
                        <div style='padding-right: 15px;'><span style='font-size: 0.85rem; color: #555;'>Cod dB (Cutie):</span> <br><span style='color: #28a745; font-size: 1.1rem; font-weight: bold;'>{p_data['oracle_box']}</span></div>
                        <div><span style='font-size: 0.85rem; color: #555;'>Cod Produs (NEXUS):</span> <br><span style='color: #6c757d; font-size: 1.1rem; font-weight: bold;'>{p_data['cod_master']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                av_pal, av_box = get_available_stock_ui(prod_name)
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("📦 Stoc PALEȚI", av_pal)
                col_s2.metric("📦 Stoc CUTII (Libere)", av_box)
                col_s3.metric("🔄 Conversie Logistică", f"{p_data['conversion']} cutii/palet")
                col_s4.metric("⚖️ Conversie Fiscală", f"{p_data['conversie_baza']} {p_data['um_baza']}/cutie")
                
                col_q1, col_q2, col_goala = st.columns([1, 1, 2])
                with col_q1: order_pal = st.number_input("Nr. PALEȚI întregi:", min_value=0, step=1, key=f'input_pal_{st.session_state.reset_counter}')
                with col_q2: order_box = st.number_input("Nr. CUTII (fracție):", min_value=0, step=1, key=f'input_box_{st.session_state.reset_counter}')
                
                if st.button("➕ Adaugă în Listă"):
                    if order_pal == 0 and order_box == 0:
                        st.warning("Introduceți o cantitate.")
                    else:
                        is_valid = calculate_delta(prod_name, order_pal, order_box)
                        if not is_valid:
                            st.error("❌ STOC INSUFICIENT pentru această cantitate!")
                        else:
                            st.session_state.schita_comanda.append({
                                "Produs": prod_name,
                                "Cod_NIR": p_data['cod_nir'],
                                "Alias_Folosit": alias_folosit,
                                "Paleti": order_pal,
                                "Cutii": order_box,
                                "Cod_Depozit_Pal": p_data['oracle_pal'],
                                "Cod_Depozit_Box": p_data['oracle_box'],
                                "UM_Baza": p_data['um_baza'],
                                "Conversie_Baza": p_data['conversie_baza']
                            })
                            st.success(f"Adăugat: {prod_name} ({order_pal} Pal, {order_box} Cutii)")
                            force_reset()
                            st.rerun()

            st.divider()

            if len(st.session_state.schita_comanda) > 0:
                st.markdown(f"#### 🛒 Produse în comanda curentă (Către: **{client_ales}**)")
                
                h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
                h1.markdown("**Produs**")
                h2.markdown("**Cod dB (Logistic)**")
                h3.markdown("**Cantitate Comandată**")
                h4.markdown("**Total Fiscal**")
                h5.markdown("**Acțiune**")
                st.markdown("<hr style='margin-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                
                for idx, item in enumerate(st.session_state.schita_comanda):
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                    
                    nume_afisare = item['Produs']
                    if item.get('Alias_Folosit'):
                        nume_afisare += f" <br><span style='color: #e67e22; font-size:0.85rem;'>(Ref: {item['Alias_Folosit']})</span>"
                    c1.markdown(nume_afisare, unsafe_allow_html=True)
                    
                    c2.markdown(f"{item['Cod_Depozit_Pal']} / {item['Cod_Depozit_Box']}")
                    c3.markdown(f"**{item['Paleti']}** Pal | **{item['Cutii']}** Cut")
                    
                    total_cutii = (item['Paleti'] * st.session_state.db[item['Produs']]['conversion']) + item['Cutii']
                    c4.markdown(f"**{total_cutii * item['Conversie_Baza']}** {item['UM_Baza']}")
                    
                    if c5.button("❌", key=f"del_row_{idx}", help="Șterge acest produs"):
                        st.session_state.schita_comanda.pop(idx)
                        st.rerun()
                
                st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    if st.button("🗑️ Golește toată Lista"):
                        st.session_state.schita_comanda = []
                        st.rerun()
                with col_btn2:
                    if st.button("👁️ Analizează & Finalizează (Auto-Convertor)", type="primary", use_container_width=True):
                        st.session_state.client_temporar_comandat = client_ales
                        st.session_state.mod_previzualizare = True
                        st.rerun()
            else:
                st.info("Schița este goală. Adăugați produse pentru a forma o comandă.")

        # --- ECRAN B: PREVIZUALIZARE & SALVARE PAYLOAD-URI SCINDATE ---
        else:
            client_ales_prev = st.session_state.client_temporar_comandat
            st.markdown("### 🔍 Previzualizare Aviz (PRISMA OPTICĂ)")
            
            st.markdown(f"""
            <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #fff;'>
                <h4 style='text-align: center; color: #003366;'>MOTOR DE OPTIMIZARE: "REGULA DIMO-NEXUS" ACTIVATĂ</h4>
                <p><b>Data:</b> {data_azi} | <b>Beneficiar:</b> {client_ales_prev} | <b>Nr. Cmd:</b> CMD-{st.session_state.order_number}</p>
                <hr>
            </div>
            """, unsafe_allow_html=True)
            
            payload_logistic_curent = []
            payload_fiscal_curent = []
            
            for item in st.session_state.schita_comanda:
                nume_oficial = item['Produs']
                P = st.session_state.db[nume_oficial]['conversion']
                L = st.session_state.db[nume_oficial]['stock_box']
                C = item['Cutii']
                pallets_ordered = item['Paleti']
                
                # --- LOGICA WMS / LOGISTIC (Regula Dimo-NEXUS) ---
                if C > 0:
                    if (P - C) < C and L < C:
                        if pallets_ordered > 0:
                            payload_logistic_curent.append({
                                "Acțiune / Cod Depozit": item['Cod_Depozit_Pal'],
                                "Cantitate": str(pallets_ordered),
                                "U.M. Logistic": "Palet Sigilat"
                            })
                        payload_logistic_curent.append({
                            "Acțiune / Cod Depozit": item['Cod_Depozit_Pal'],
                            "Cantitate": "1",
                            "U.M. Logistic": f"Palet (Optimizare: EXTRAGE {P - C} cutii și încarcă restul de {C})"
                        })
                    else:
                        if pallets_ordered > 0:
                            payload_logistic_curent.append({
                                "Acțiune / Cod Depozit": item['Cod_Depozit_Pal'],
                                "Cantitate": str(pallets_ordered),
                                "U.M. Logistic": "Palet Sigilat"
                            })
                        if C <= L:
                            payload_logistic_curent.append({
                                "Acțiune / Cod Depozit": item['Cod_Depozit_Box'],
                                "Cantitate": str(C),
                                "U.M. Logistic": "Cutie Fracție (Culese din stoc liber)"
                            })
                        else:
                            if L > 0:
                                payload_logistic_curent.append({
                                    "Acțiune / Cod Depozit": item['Cod_Depozit_Box'],
                                    "Cantitate": str(L),
                                    "U.M. Logistic": "Cutie Fracție (Golește stoc liber)"
                                })
                            payload_logistic_curent.append({
                                "Acțiune / Cod Depozit": item['Cod_Depozit_Box'],
                                "Cantitate": str(C - L),
                                "U.M. Logistic": "Cutie Fracție (Din palet nou desfăcut)"
                            })
                else:
                    if pallets_ordered > 0:
                        payload_logistic_curent.append({
                            "Acțiune / Cod Depozit": item['Cod_Depozit_Pal'],
                            "Cantitate": str(pallets_ordered),
                            "U.M. Logistic": "Palet Sigilat"
                        })

                # --- LOGICA SMARTBILL / FISCAL ---
                total_cutii = (pallets_ordered * P) + C
                total_unitati_baza = total_cutii * item['Conversie_Baza']
                
                referinta = f"Ref: {item['Alias_Folosit']}" if item.get('Alias_Folosit') else "-"
                payload_fiscal_curent.append({
                    "Cod SB (NIR)": item['Cod_NIR'],
                    "Nomenclator Oficial": nume_oficial,
                    "Cantitate (U.M.)": f"{total_unitati_baza} {item['UM_Baza']}",
                    "Observații (Alias)": referinta
                })

            col_prism1, col_prism2 = st.columns(2)
            
            with col_prism1:
                st.markdown("#### 🚚 Liniile WMS (Tableta Depozit)")
                st.dataframe(pd.DataFrame(payload_logistic_curent), hide_index=True, use_container_width=True)

            with col_prism2:
                st.markdown("#### 🧾 Date Fiscale (Spre SmartBill)")
                st.dataframe(pd.DataFrame(payload_fiscal_curent), hide_index=True, use_container_width=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔙 Întoarce-te (Editează coșul)"):
                    st.session_state.mod_previzualizare = False
                    st.rerun()
            with col_b2:
                if st.button("🚀 CONFIRMĂ ȘI LANSEAZĂ SPRE DEPOZIT", type="primary", use_container_width=True):
                    
                    for item in st.session_state.schita_comanda:
                        prod = item['Produs']
                        P = st.session_state.db[prod]['conversion']
                        C = item['Cutii']
                        pallets_ordered = item['Paleti']
                        L = st.session_state.db[prod]['stock_box']
                        
                        if C > 0:
                            if (P - C) < C and L < C:
                                st.session_state.db[prod]['stock_pal'] -= (pallets_ordered + 1)
                                st.session_state.db[prod]['stock_box'] += (P - C)
                            else:
                                total_units_to_subtract = (pallets_ordered * P) + C
                                stoc_curent = get_total_boxes(prod)
                                stoc_ramas = stoc_curent - total_units_to_subtract
                                st.session_state.db[prod]['stock_pal'] = stoc_ramas // P
                                st.session_state.db[prod]['stock_box'] = stoc_ramas % P
                        else:
                            st.session_state.db[prod]['stock_pal'] -= pallets_ordered

                    st.session_state.istoric_comenzi_live.append({
                        "Comanda": f"CMD-{st.session_state.order_number}",
                        "Client": client_ales_prev,
                        "Linii_Logistice": len(payload_logistic_curent),
                        "Linii_Fiscale": len(payload_fiscal_curent),
                        "Payload_Logistic": payload_logistic_curent,
                        "Payload_Fiscal": payload_fiscal_curent,
                        "Status": "Așteaptă Încărcare",
                        "Data_Ora": datetime.now(pytz.timezone('Europe/Bucharest')).strftime("%H:%M:%S")
                    })

                    st.success("✅ Comanda a fost transmisă! Optimizările WMS au fost aplicate.")
                    st.toast(f"📧 Notificare email trimisă către: {client_ales_prev} (Conceptual)", icon="✉️")
                    
                    st.session_state.order_number += 1
                    st.session_state.schita_comanda = []
                    st.session_state.mod_previzualizare = False
                    time.sleep(2.5)
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
                    <p style='margin-bottom: 0;'><b>Status:</b> {cmd['Status']} | <b>Ora Lansării:</b> {cmd['Data_Ora']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📦 Vezi instrucțiunile primite de Stivuitorist"):
                    st.table(pd.DataFrame(cmd['Payload_Logistic']))
                
                col_btn_a, col_btn_b = st.columns([1, 2])
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
                            if st.button("🖨️ EMITE AVIZUL (Trimite U.M. la SmartBill)", type="primary", key=f"emit_{idx}"):
                                st.session_state.istoric_comenzi_live[idx]['document_emis'] = True
                                st.session_state.istoric_comenzi_live[idx]['Status'] = "Finalizat. Trimis SB."
                                st.success("✅ Avizul se tipărește! Datele comerciale convertite au fost transmise către SmartBill.")
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.info("Aviz Emis. Linii comerciale finalizate și trimise la SmartBill.")
                st.divider()

    # ==========================================
    # TAB 3: RECEPȚIE
    # ==========================================
    with tab3:
        st.markdown("### 📥 Sincronizare Recepții")
        st.info("🚧 În producție, acest ecran va fi populat cu NIR-urile noi emise de SmartBill/WMS.")

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
        st.subheader("🔴 LIVE FEED: Comenzi Noi (Depozit)")
        if len(st.session_state.istoric_comenzi_live) > 0:
            df_live = pd.DataFrame(st.session_state.istoric_comenzi_live)
            st.dataframe(df_live[['Comanda', 'Client', 'Linii_Logistice', 'Status', 'Data_Ora']], use_container_width=True, hide_index=True)
        else:
            st.info("Nicio comandă nouă lansată astăzi.")
            
        st.divider()
        
        st.subheader("2. Analiză Stoc Punctual")
        mgr_prod = st.selectbox("Selectare Produs:", list(st.session_state.db.keys()))
        p_val = st.session_state.db[mgr_prod]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Paleți Intacți", p_val['stock_pal'])
        c2.metric("Cutii Libere", p_val['stock_box'])
        c3.metric("Conversie WMS", f"{p_val['conversion']} cutii/palet")
        c4.metric("Conversie Fiscală", f"{p_val['conversie_baza']} {p_val['um_baza']}/cutie")
        
        if p_val['stock_box'] > (p_val['conversion'] * 0.7):
            st.error(f"🔴 ATENȚIE: Aveți prea multe cutii libere ({p_val['stock_box']}).")
        elif p_val['stock_box'] > 0:
            st.warning("🟠 INFO: Există cutii libere în depozit.")
        else:
            st.success("🟢 OPTIM: Nu aveți fracții desfăcute în depozit.")
                
    with tab_an:
        col_m1, col_m2 = st.columns([2, 2])
        with col_m1: analiza_client = st.selectbox("Selectează Client:", clients_mock)
        with col_m2: analiza_produs = st.selectbox("Selectează Produs pt. istoric:", list(st.session_state.db.keys()), key="mgr_prod_an")
        
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
