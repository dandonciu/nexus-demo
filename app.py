import streamlit as st
import time
from datetime import datetime
import math
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NEXUS B2B - MASTER DEV", page_icon="⚙️", layout="wide")

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
                ⚙️ NEXUS [Master DEV]
            </h1>
            <p style="margin: 0; padding: 0; font-style: italic; color: #a8c5e8; font-size: 1.1rem; margin-top: -5px;">
                Rezolvă problemele, nu le creează.
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

# --- BAZA DE DATE MOCK ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "Role Autocut Albe TAD 220m": {
            "cod_master": "MST-BKTp721", "cod_nir": "NIR-4451",
            "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 3, "stock_box": 0, "conversion": 64,
            "descriere": "Role din celuloză pură 100%, 2 straturi. Greutate palet: 210kg.",
            "livrari_totale": pd.DataFrame({
                "Client": ["🏢 SC CORPORATIA ALPHA SRL", "🏢 SC CORPORATIA ALPHA SRL", "🏢 BETA DISTRIBUTION"],
                "Data": ["10-01-2024", "15-02-2024", "08-01-2024"],
                "Volum_Paleti": [12, 15, 20],
                "Status_Plata": ["Achitat", "Achitat", "Achitat"]
            })
        },
        "Lavete Craft Puromore Blue": {
            "cod_master": "MST-70117",  "cod_nir": "NIR-8820",
            "oracle_pal": "PAL 70117", "oracle_box": "70117",
            "stock_pal": 1, "stock_box": 10, "conversion": 120,
            "descriere": "Lavete industriale rezistente la solvenți, culoare albastră, 500 porții/rolă.",
            "livrari_totale": pd.DataFrame({
                "Client": ["🏢 SC CORPORATIA ALPHA SRL", "🏢 BETA DISTRIBUTION"],
                "Data": ["05-01-2024", "10-01-2024"],
                "Volum_Paleti": [5, 15],
                "Status_Plata": ["Achitat", "Restanță"]
            })
        }
    }

# --- TRANSLATORUL DE ALIAS-URI ---
aliases_map = {
    "Cârpe albastre (Client 1)": "Lavete Craft Puromore Blue",
    "Role industriale curățenie (Client 2)": "Lavete Craft Puromore Blue",
    "Hârtie Mâini albă (General)": "Role Autocut Albe TAD 220m",
    "Role ștergere Z (Client 3)": "Role Autocut Albe TAD 220m"
}

clients_mock = ["🏢 SC CORPORATIA ALPHA SRL", "🏢 BETA DISTRIBUTION", "🏢 Client 1", "🏢 Client 2"]

# --- FUNCTII STOC ---
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

# --- ECRAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 NEXUS</h1>", unsafe_allow_html=True)
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
    with col_titlu: st.title("⚡ NEXUS Operațional")
    with col_cmd:
        data_azi = datetime.now().strftime("%d.%m.%Y")
        st.info(f"**Nr. Cmd:** {st.session_state.order_number}  \n**Data:** {data_azi}")
        
    tab1, tab2, tab3 = st.tabs(["🛒 Lansare Comandă", "🚚 Status & Documente", "📥 Recepție Marfă"])
    
    # --- TAB 1: LANSARE COMANDA ---
    with tab1:
        client_ales = st.selectbox("1. Selectează Beneficiarul:", clients_mock)
        
        # Alerta Masina Rampa
        comenzi_pending = [cmd for cmd in st.session_state.istoric_comenzi_live if cmd.get('status_incarcat', False) and not cmd.get('document_emis', False)]
        if len(comenzi_pending) > 0:
            st.markdown(f"""
            <div style='background-color: #fff3f3; border-left: 5px solid #dc3545; padding: 15px; margin-top: 10px; margin-bottom: 20px; border-radius: 4px; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <div style='font-size: 2rem; margin-right: 15px;'>🚨</div>
                <div>
                    <h4 style='color: #dc3545; margin: 0;'>ACȚIUNE NECESARĂ: {len(comenzi_pending)} mașină(i) așteaptă actele la rampă!</h4>
                    <p style='margin: 0; font-size: 0.95rem; color: #555;'>Treceți în tab-ul <b>'Status & Documente'</b> pentru a emite Avizul.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        if not st.session_state.mod_previzualizare:
            st.markdown("### 📋 Formare Schiță Comandă")
            with st.container():
                all_options = list(st.session_state.db.keys()) + list(aliases_map.keys())
                selected_option = st.selectbox("Alege Produsul (sau tastează denumirea clientului):", all_options, on_change=force_reset)
                
                if selected_option in aliases_map:
                    prod_name = aliases_map[selected_option]
                    alias_folosit = selected_option
                    st.success(f"🔄 Sistemul a tradus: **{selected_option}** = **{prod_name}**")
                else:
                    prod_name = selected_option
                    alias_folosit = None
                
                p_data = st.session_state.db[prod_name]
                
                st.markdown(f"""
                <div style='background-color: #f0f7f4; padding: 20px; border-radius: 8px; border-left: 5px solid #28a745; margin-bottom: 20px;'>
                    <div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>
                        <div style='flex: 1; min-width: 180px; margin-bottom: 10px;'>
                            <div style='font-size: 0.85rem; color: #555;'>Cod produs (NEXUS)</div>
                            <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['cod_master']}</div>
                        </div>
                        <div style='flex: 1; min-width: 200px; margin-bottom: 10px;'>
                            <div style='font-size: 0.85rem; color: #555;'>Cod dB Depozit (Palet)</div>
                            <div style='font-size: 1.4rem; color: #28a745; font-weight: bold;'>{p_data['oracle_pal']}</div>
                        </div>
                        <div style='flex: 1; min-width: 150px; margin-bottom: 10px;'>
                            <div style='font-size: 0.85rem; color: #555;'>Cod dB Depozit (Cutie)</div>
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
                
                col_q1, col_q2, _ = st.columns([1, 1, 1])
                with col_q1: order_pal = st.number_input("Nr. PALEȚI:", min_value=0, step=1, key=f'input_pal_{st.session_state.reset_counter}')
                with col_q2: order_box = st.number_input("Nr. CUTII:", min_value=0, step=1, key=f'input_box_{st.session_state.reset_counter}')
                
                if st.button("➕ Adaugă în Listă"):
                    if order_pal == 0 and order_box == 0: st.warning("Introduceți o cantitate.")
                    elif calculate_delta(prod_name, order_pal, order_box):
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

            if len(st.session_state.schita_comanda) > 0:
                st.markdown(f"#### 🛒 Produse în comanda curentă (Către: {client_ales})")
                lista_afisare = []
                for item in st.session_state.schita_comanda:
                    nume_aviz = item['Prod_Oficial']
                    if item['Alias_Folosit']: nume_aviz += f" (Ref: {item['Alias_Folosit']})"
                    lista_afisare.append({"Produs": nume_aviz, "Paleti": str(item['Paleti']), "Cutii": str(item['Cutii'])})
                
                st.dataframe(pd.DataFrame(lista_afisare), use_container_width=True, hide_index=True)
                
                c_b1, c_b2 = st.columns([1, 3])
                with c_b1:
                    if st.button("🗑️ Golește Lista"):
                        st.session_state.schita_comanda = []
                        st.rerun()
                with c_b2:
                    if st.button("👁️ Previzualizare & Finalizare", type="primary", use_container_width=True):
                        st.session_state.mod_previzualizare = True
                        st.rerun()

        else:
            st.markdown("### 🔍 Previzualizare Aviz (Înainte de Trimitere)")
            st.markdown(f"""
            <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #fff;'>
                <h4 style='text-align: center; color: #003366;'>PROIECT AVIZ EXPEDIȚIE - NEXUS</h4>
                <p><b>Data:</b> {data_azi}<br><b>Client:</b> {client_ales}<br><b>Nr. Comandă Interne:</b> CMD-{st.session_state.order_number}</p>
                <hr>
            </div>
            """, unsafe_allow_html=True)
            
            lista_print = []
            for item in st.session_state.schita_comanda:
                nume_aviz = item['Prod_Oficial']
                if item['Alias_Folosit']: nume_aviz += f" [Ref. Client: {item['Alias_Folosit']}]"
                lista_print.append({"Produs Facturat / Aviz": nume_aviz, "Paleti": str(item['Paleti']), "Cutii": str(item['Cutii'])})
            st.table(pd.DataFrame(lista_print))
            
            st.warning("⚠️ Odată lansată, comanda blochează stocul.")
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("🔙 Întoarce-te"):
                    st.session_state.mod_previzualizare = False
                    st.rerun()
            with c_b2:
                if st.button("🚀 CONFIRMĂ ȘI LANSEAZĂ SPRE DEPOZIT", type="primary", use_container_width=True):
                    totaluri_cos = {}
                    for item in st.session_state.schita_comanda:
                        prod = item['Prod_Oficial']
                        cutii_total_item = (item['Paleti'] * st.session_state.db[prod]['conversion']) + item['Cutii']
                        totaluri_cos[prod] = totaluri_cos.get(prod, 0) + cutii_total_item
                        
                    for prod, cutii_de_scazut in totaluri_cos.items():
                        stoc_curent = get_total_boxes(prod)
                        stoc_ramas = stoc_curent - cutii_de_scazut
                        conv = st.session_state.db[prod]['conversion']
                        st.session_state.db[prod]['stock_pal'] = stoc_ramas // conv
                        st.session_state.db[prod]['stock_box'] = stoc_ramas % conv
                    
                    st.session_state.istoric_comenzi_live.append({
                        "Comanda": f"CMD-{st.session_state.order_number}",
                        "Client": client_ales,
                        "Articole": len(st.session_state.schita_comanda),
                        "Status": "Așteaptă Încărcare",
                        "Data_Ora": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    st.session_state.order_number += 1
                    st.session_state.schita_comanda = []
                    st.session_state.mod_previzualizare = False
                    st.success("✅ Comanda a fost trimisă!")
                    time.sleep(1.5)
                    st.rerun()

    # --- TAB 2: STATUS & DOCUMENTE ---
    with tab2:
        st.markdown("### 🚚 Confirmare Depozit & Emitere Documente")
        comenzi_lansate = st.session_state.istoric_comenzi_live
        if len(comenzi_lansate) == 0:
            st.info("Nicio comandă nu a fost lansată încă spre depozit.")
        else:
            for idx, cmd in enumerate(comenzi_lansate):
                cu_status_incarcat = cmd.get('status_incarcat', False)
                bg_color = "#f9fff9" if cu_status_incarcat else "#fffdf5"
                st.markdown(f"<div style='background-color: {bg_color}; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'><h4 style='margin-top: 0; color: #003366;'>{cmd['Comanda']} - {cmd['Client']}</h4><p style='margin-bottom: 0;'><b>Articole:</b> {cmd['Articole']} | <b>Status:</b> {cmd['Status']}</p></div>", unsafe_allow_html=True)
                
                c_btn_a, c_btn_b = st.columns(2)
                with c_btn_a:
                    if not cu_status_incarcat:
                        if st.button("📲 Simulare: Confirmat Depozit", key=f"sim_dep_{idx}"):
                            st.session_state.istoric_comenzi_live[idx]['Status'] = "Încărcat. Gata de printare."
                            st.session_state.istoric_comenzi_live[idx]['status_incarcat'] = True
                            st.rerun()
                    else: st.success("✅ Marfă Încărcată")
                with c_btn_b:
                    if cu_status_incarcat:
                        if not cmd.get('document_emis', False):
                            if st.button("🖨️ EMITE AVIZUL (Și trimite la SmartBill)", type="primary", key=f"emit_{idx}"):
                                st.session_state.istoric_comenzi_live[idx]['document_emis'] = True
                                st.session_state.istoric_comenzi_live[idx]['Status'] = "Finalizat. Trimis SB."
                                st.success("✅ Aviz tipărit și trimis!")
                                time.sleep(1.5)
                                st.rerun()
                        else: st.info("Documente finalizate.")
                st.divider()

    with tab3:
        st.markdown("### 📥 Sincronizare Recepții (Așteptare SmartBill)")

# ==========================================
# --- APLICAȚIA MANAGER ---
# ==========================================
elif st.session_state.role == "manager":
    st.title("📈 NEXUS Dashboard Manager")
    tab_op, tab_an = st.tabs(["⚡ A. Situație Operativă (Birou)", "📊 B. Analiză Generală (Ședințe)"])
    
    with tab_op:
        st.subheader("🔴 LIVE FEED: Comenzi Noi (Depozit)")
        if len(st.session_state.istoric_comenzi_live) > 0:
            st.dataframe(pd.DataFrame(st.session_state.istoric_comenzi_live), use_container_width=True, hide_index=True)
        else: st.info("Nicio comandă nouă lansată astăzi.")
        st.divider()
        
        st.subheader("Analiză Stoc Punctual")
        mgr_prod = st.selectbox("Selectare Produs:", list(st.session_state.db.keys()))
        p_val = st.session_state.db[mgr_prod]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Paleți Intacți", p_val['stock_pal'])
        c2.metric("Cutii Libere", p_val['stock_box'])
        c3.metric("Conversie", f"{p_val['conversion']} cutii/palet")
        billed = math.ceil(get_total_boxes(mgr_prod) / p_val['conversion'])
        c4.metric("Facturare Depozit", f"{billed} paleți")

    with tab_an:
        c_m1, c_m2, c_m3 = st.columns([2, 2, 1])
        with c_m1: analiza_client = st.selectbox("Selectează Client / Filială:", clients_mock)
        with c_m2: analiza_produs = st.selectbox("Selectează Produs:", list(st.session_state.db.keys()), key="mgr_prod_an")
        with c_m3: raport = st.selectbox("Raport", ["Evoluție Volume"])
        
        if raport == "Evoluție Volume":
            df_toate = st.session_state.db[analiza_produs]["livrari_totale"]
            df_filtrat = df_toate[df_toate['Client'] == analiza_client]
            if df_filtrat.empty: st.warning("Nu există date.")
            else:
                fig = px.bar(df_filtrat, x='Data', y='Volum_Paleti', color='Status_Plata', text='Volum_Paleti', title="Volum Paleți / Dată")
                fig.update_layout(xaxis_type='category')
                st.plotly_chart(fig, use_container_width=True)
