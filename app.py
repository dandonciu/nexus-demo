import streamlit as st
import time
from datetime import datetime
import math
import pandas as pd

st.set_page_config(page_title="NEXUS B2B - DEV", page_icon="⚙️", layout="wide")

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
                ⚙️ NEXUS [Laborator]
            </h1>
            <p style="margin: 0; padding: 0; font-style: italic; color: #a8c5e8; font-size: 1.1rem; margin-top: -5px;">
                Rezolvă problemele, nu le creează.
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; padding: 0; font-weight: bold; font-size: 1.3rem; letter-spacing: 0.5px;">
                NOVA SAFE
            </p>
            <p style="margin: 0; padding: 0; font-size: 0.95rem; color: #d0e1f9;">
                Modul de Testare Avansată
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
    st.session_state.logged_in = True # Fortam login pt testare rapida
    st.session_state.role = "angajat"

if 'order_number' not in st.session_state:
    st.session_state.order_number = 1001

if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

if 'schita_comanda' not in st.session_state:
    st.session_state.schita_comanda = []
    
if 'mod_previzualizare' not in st.session_state:
    st.session_state.mod_previzualizare = False

def force_reset():
    st.session_state.reset_counter += 1

# BAZA DE DATE PRODUSE
if 'db' not in st.session_state:
    st.session_state.db = {
        "Role Autocut Albe TAD 220m": {
            "cod_master": "MST-BKTp721", "cod_nir": "NIR-4451",
            "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 3, "stock_box": 0, "conversion": 64
        },
        "Lavete Craft Puromore Blue": {
            "cod_master": "MST-70117",  "cod_nir": "NIR-8820",
            "oracle_pal": "PAL 70117", "oracle_box": "70117",
            "stock_pal": 1, "stock_box": 10, "conversion": 120
        }
    }

# [NOU] DICȚIONARUL DE SINONIME (TRANSLATORUL)
aliases_map = {
    "Cârpe albastre (Client 1)": "Lavete Craft Puromore Blue",
    "Role industriale curățenie (Client 2)": "Lavete Craft Puromore Blue",
    "Hârtie Mâini albă (General)": "Role Autocut Albe TAD 220m",
    "Role ștergere Z (Client 3)": "Role Autocut Albe TAD 220m"
}

clients_mock = ["🏢 SC CORPORATIA ALPHA SRL", "🏢 BETA DISTRIBUTION", "🏢 Client 1", "🏢 Client 2"]

def get_total_boxes(prod_key):
    p = st.session_state.db[prod_key]
    return (p['stock_pal'] * p['conversion']) + p['stock_box']

def get_available_stock_ui(prod_key):
    total_db = get_total_boxes(prod_key)
    in_cart = sum([(item['Paleti'] * st.session_state.db[prod_key]['conversion']) + item['Cutii'] 
                   for item in st.session_state.schita_comanda if item['Prod_Oficial'] == prod_key])
    rem = total_db - in_cart
    conv = st.session_state.db[prod_key]['conversion']
    return rem // conv, rem % conv

def calculate_delta(prod_key, cmd_pal, cmd_box):
    total_stock = get_total_boxes(prod_key)
    in_cart = sum([(item['Paleti'] * st.session_state.db[prod_key]['conversion']) + item['Cutii'] 
                   for item in st.session_state.schita_comanda if item['Prod_Oficial'] == prod_key])
    p = st.session_state.db[prod_key]
    total_cmd = (cmd_pal * p['conversion']) + cmd_box + in_cart
    if total_cmd > total_stock: return None
    return True

# ==========================================
# --- APLICAȚIA ANGAJAT ---
# ==========================================
if st.session_state.role == "angajat":
    col_titlu, col_cmd = st.columns([4, 1])
    with col_titlu: st.title("⚡ NEXUS - Flux Comenzi")
    with col_cmd: st.info(f"**Nr. Cmd:** {st.session_state.order_number}")
        
    client_ales = st.selectbox("1. Selectează Beneficiarul:", clients_mock)
    
    # --- ECRAN A: ADĂUGARE ÎN SCHIȚĂ ---
    if not st.session_state.mod_previzualizare:
        st.markdown("### 📋 Formare Schiță Comandă")
        
        with st.container():
            # [UPDATE] Combinăm Numele Oficiale cu Dicționarul
            all_options = list(st.session_state.db.keys()) + list(aliases_map.keys())
            
            selected_option = st.selectbox("2. Alege Produsul (sau tastează denumirea clientului):", all_options, on_change=force_reset)
            
            # Logica de traducere
            if selected_option in aliases_map:
                prod_name = aliases_map[selected_option]
                alias_folosit = selected_option
                st.success(f"🔄 Sistemul a tradus automat: **{selected_option}** = **{prod_name}**")
            else:
                prod_name = selected_option
                alias_folosit = None
            
            p_data = st.session_state.db[prod_name]
            
            # Afișare coduri depozit
            st.markdown(f"""
            <div style='background-color: #f0f7f4; padding: 15px; border-radius: 5px; border-left: 5px solid #28a745; margin-bottom: 15px;'>
                <b>Cod dB Depozit (Palet):</b> {p_data['oracle_pal']} | <b>Cod dB Depozit (Cutie):</b> {p_data['oracle_box']}
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
                    st.warning("Introduceți o cantitate.")
                else:
                    if calculate_delta(prod_name, order_pal, order_box):
                        st.session_state.schita_comanda.append({
                            "Prod_Oficial": prod_name,
                            "Alias_Folosit": alias_folosit,
                            "Paleti": order_pal,
                            "Cutii": order_box
                        })
                        st.success("Adăugat cu succes!")
                        force_reset()
                        st.rerun()
                    else: st.error("❌ STOC INSUFICIENT!")

        st.divider()

        # ZONA SCHIȚĂ
        if len(st.session_state.schita_comanda) > 0:
            st.markdown(f"#### 🛒 Produse în coș (Către: {client_ales})")
            
            # Formatăm datele pentru afișare frumoasă
            lista_afisare = []
            for item in st.session_state.schita_comanda:
                nume_aviz = item['Prod_Oficial']
                if item['Alias_Folosit']: nume_aviz += f" (Ref: {item['Alias_Folosit']})"
                
                lista_afisare.append({
                    "Denumire Produs (Ce apare pe Aviz)": nume_aviz,
                    "Paleti": str(item['Paleti']),
                    "Cutii": str(item['Cutii'])
                })
                
            st.dataframe(pd.DataFrame(lista_afisare), use_container_width=True, hide_index=True)
            
            if st.button("👁️ Previzualizare Aviz & Finalizare", type="primary"):
                st.session_state.mod_previzualizare = True
                st.rerun()

    # --- ECRAN B: PREVIZUALIZARE ---
    else:
        st.markdown("### 🔍 Previzualizare Aviz (Cum se tipărește)")
        
        lista_print = []
        for item in st.session_state.schita_comanda:
            nume_aviz = item['Prod_Oficial']
            if item['Alias_Folosit']: nume_aviz += f" \n[Ref. Client: {item['Alias_Folosit']}]"
            lista_print.append({"Produs Facturat / Aviz": nume_aviz, "Paleti": str(item['Paleti']), "Cutii": str(item['Cutii'])})
            
        st.table(pd.DataFrame(lista_print))
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔙 Întoarce-te"):
                st.session_state.mod_previzualizare = False
                st.rerun()
        with col_b2:
            if st.button("🚀 Trimite la Depozit (Codurile oficiale)", type="primary"):
                st.success("Trimis! Depozitul a primit comanda strict pe codurile NEXUS.")
                # Curățare
                st.session_state.order_number += 1
                st.session_state.schita_comanda = []
                st.session_state.mod_previzualizare = False
                time.sleep(2)
                st.rerun()

