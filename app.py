import streamlit as st
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import os
import csv
import base64
from fpdf import FPDF

# --- INITIALIZARE FOLDERE EXPORT ---
EXPORT_DIR = "exports"
PDF_DIR = os.path.join(EXPORT_DIR, "pdf_docs")
WMS_DIR = os.path.join(EXPORT_DIR, "wms_payloads")

for folder in [EXPORT_DIR, PDF_DIR, WMS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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
                Rezolva probleme, nu le creeaza. (Auto-Convertor: Logistic-Fiscal)
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; padding: 0; font-weight: bold; font-size: 1.3rem; letter-spacing: 0.5px;">
                NOVA SAFE SRL
            </p>
            <p style="margin: 0; padding: 0; font-size: 0.95rem; color: #d0e1f9;">
                Sistem Integrat de Gestiune Operativa
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DATE REALE: FURNIZOR & CLIENTI ---
furnizor_data = {
    "Nume": "NOVA SAFE SRL",
    "RegCom": "J2015015825407", "CIF": "RO35368260",
    "Adresa": "Str. Turturelelor 11B, Bucuresti",
    "Banca": "Banca Transilvania", "IBAN": "RO72BTRLRONCRT0363372001"
}

clients_data = {
    "S.C. SIDE GRUP S.R.L.": {
        "RegCom": "J2003000200023", "CIF": "RO15216895",
        "Adresa": "Felnac, Nr.1000, judet Arad",
        "Banca": "UNICREDIT BANK S.A. ARAD", "IBAN": "RO20 BACX 0066 4409 4144 5000"
    },
    "DSCM TECH SRL": {
        "RegCom": "J17/1179/2013", "CIF": "RO32278456",
        "Adresa": "Com T.Vladimirescu, str.Principala 993, Galati",
        "Banca": "Raiffeisen Bank", "IBAN": "-"
    }
}

client_aliases = {
    "S.C. SIDE GRUP S.R.L.": {"Prosoape Verzi Pliate": "Prosoape V verzi"},
    "DSCM TECH SRL": {"Role Albe Stergere": "Role autocut albe TAD 220m"}
}

# --- DB BUFFER ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "Prosoape V verzi": {
            "cod_nir": "NIR-209520", "oracle_pal": "PAL NV710", "oracle_box": "NV710",
            "stock_pal": 4, "stock_box": 15, "conversion": 32,
            "um_baza": "Pachete", "conversie_baza": 20
        },
        "Role autocut albe TAD 220m": {
            "cod_nir": "NIR-156350", "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 4, "stock_box": 32, "conversion": 48,
            "um_baza": "Role", "conversie_baza": 6
        },
        "Saci menaj 120L negri LDPE": {
            "cod_nir": "NIR-211125", "oracle_pal": "PAL IVFLX120LD-N", "oracle_box": "IVFLX120LD-N",
            "stock_pal": 5, "stock_box": 20, "conversion": 60,
            "um_baza": "Role", "conversie_baza": 15
        }
    }

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'order_number' not in st.session_state: st.session_state.order_number = 218395
if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
if 'schita_comanda' not in st.session_state: st.session_state.schita_comanda = []
if 'mod_previzualizare' not in st.session_state: st.session_state.mod_previzualizare = False
if 'istoric_comenzi_live' not in st.session_state: st.session_state.istoric_comenzi_live = []

def force_reset(): st.session_state.reset_counter += 1

def get_total_boxes(prod_key):
    p = st.session_state.db[prod_key]
    return (p['stock_pal'] * p['conversion']) + p['stock_box']

def get_available_stock_ui(prod_key):
    total_db = get_total_boxes(prod_key)
    in_cart = sum([(item.get('Paleti', 0) * st.session_state.db[prod_key]['conversion']) + item.get('Cutii', 0) 
                   for item in st.session_state.schita_comanda if item.get('Produs') == prod_key])
    rem = total_db - in_cart
    return rem // st.session_state.db[prod_key]['conversion'], rem % st.session_state.db[prod_key]['conversion']

def calculate_delta(prod_key, cmd_pal, cmd_box):
    return ((cmd_pal * st.session_state.db[prod_key]['conversion']) + cmd_box + 
            sum([(i['Paleti'] * st.session_state.db[prod_key]['conversion']) + i['Cutii'] for i in st.session_state.schita_comanda if i['Produs'] == prod_key])) <= get_total_boxes(prod_key)

def clean_text(txt):
    replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
    for k, v in replacements.items(): txt = txt.replace(k, v)
    return txt

# ================= GENERARE PDF & CSV =================
def generate_wms_csv(order_no, payload_logistic):
    filepath = os.path.join(WMS_DIR, f"WMS_EXPORT_SCF_{order_no}.csv")
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Order Code", "Product Code", "Quantity", "Packing Type"])
        for row in payload_logistic:
            writer.writerow([f"SCF-{order_no}", row["Acțiune / Cod Depozit"], row["Cantitate"], row["U.M. Logistic"]])
    return filepath

def generate_pdf_aviz(order_no, client_name, payload_fiscal):
    pdf = FPDF()
    pdf.add_page()
    
    # Header - Split FURNIZOR / CLIENT
    c_data = clients_data[client_name]
    f_data = furnizor_data
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 8, clean_text(f"FURNIZOR: {f_data['Nume']}"), border=0, ln=0)
    pdf.cell(10, 8, "", border=0, ln=0)
    pdf.cell(90, 8, clean_text(f"CUMPARATOR: {client_name}"), border=0, ln=1)
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(90, 5, f"CIF: {f_data['CIF']} | J: {f_data['RegCom']}", ln=0)
    pdf.cell(10, 5, "", ln=0)
    pdf.cell(90, 5, f"CIF: {c_data['CIF']} | J: {c_data['RegCom']}", ln=1)
    
    pdf.cell(90, 5, clean_text(f"Adresa: {f_data['Adresa']}"), ln=0)
    pdf.cell(10, 5, "", ln=0)
    pdf.cell(90, 5, clean_text(f"Adresa: {c_data['Adresa']}"), ln=1)
    
    pdf.ln(10)
    
    # Titlu
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text("AVIZ DE INSOTIRE A MARFII"), align='C', ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Seria NEXUS Nr. {order_no}", align='C', ln=1)
    pdf.cell(0, 6, f"Data: {datetime.now(ZoneInfo('Europe/Bucharest')).strftime('%d.%m.%Y')}", align='C', ln=1)
    pdf.ln(5)
    
    # Tabel Linii
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(15, 8, "Nr.", 1, 0, 'C')
    pdf.cell(115, 8, "Denumire Produse", 1, 0, 'C')
    pdf.cell(20, 8, "U.M.", 1, 0, 'C')
    pdf.cell(40, 8, "Cantitate", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
    for i, item in enumerate(payload_fiscal):
        pdf.cell(15, 8, str(i+1), 1, 0, 'C')
        pdf.cell(115, 8, clean_text(item['Nomenclator Oficial'][:65]), 1, 0)
        u_m = item['Cantitate (U.M.)'].split(' ')[1]
        qty = item['Cantitate (U.M.)'].split(' ')[0]
        pdf.cell(20, 8, u_m, 1, 0, 'C')
        pdf.cell(40, 8, qty, 1, 1, 'C')
        
    pdf.ln(15)
    
    # Footer - Semnaturi si Auto
    pdf.set_font("Arial", '', 9)
    pdf.cell(90, 5, "Date privind expeditia:", ln=1)
    pdf.cell(90, 5, "Nume Delegat: .......................................", ln=1)
    pdf.cell(90, 5, "Mijloc auto nr: ........................................", ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 7)
    pdf.multi_cell(0, 4, clean_text("Prezentul document tine loc de Certificat de Origine si Calitate. Marfa ramane proprietatea Nova Safe SRL pana la achitarea integrala."))
    
    filepath = os.path.join(PDF_DIR, f"AVIZ_{order_no}.pdf")
    pdf.output(filepath)
    return filepath

def display_pdf(file_path):
    with open(file_path, "rb") as f: base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# ================= INTERFATA APP =================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("Logheaza-te cu parola: 'angajat'")
        with st.form("login_form"):
            pwd = st.text_input("Parola", type="password")
            if st.form_submit_button("Log In (Enter)"):
                if pwd == "angajat":
                    st.session_state.logged_in, st.session_state.role = True, pwd
                    st.rerun()
    st.stop()

col_titlu, col_cmd = st.columns([4, 1])
with col_titlu: st.title("⚡ NEXUS Operațional")
with col_cmd:
    st.info(f"**Nr. Cmd:** SCF-{st.session_state.order_number}  \n**Data:** {datetime.now(ZoneInfo('Europe/Bucharest')).strftime('%d.%m.%Y')}")

tab1, tab2 = st.tabs(["🛒 Schiță Comandă", "🚚 Rampa & Print Acte"])

with tab1:
    if not st.session_state.mod_previzualizare:
        st.markdown("<h4 style='color: #d9534f; margin-bottom: 5px;'>1. Selectează Beneficiarul:</h4>", unsafe_allow_html=True)
        client = st.selectbox("Client", list(clients_data.keys()), key="cli", label_visibility="collapsed")
        
        produse = list(st.session_state.db.keys()) + list(client_aliases.get(client, {}).keys())
        st.markdown("<h4 style='color: #d9534f; margin-top: 15px; margin-bottom: 5px;'>2. Alege Produsul:</h4>", unsafe_allow_html=True)
        prod_sel = st.selectbox("Produs", produse, on_change=force_reset, key="prd", label_visibility="collapsed")
        
        real_prod = client_aliases.get(client, {}).get(prod_sel, prod_sel)
        p_data = st.session_state.db[real_prod]
        
        st.markdown(f"""
        <div style='background-color: #f0f7f4; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745; margin-top: 15px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between;'>
                <div><span style='color: #555;'>Cod Fiscal (NIR):</span> <br><span style='color: #28a745; font-weight: bold;'>{p_data['cod_nir']}</span></div>
                <div><span style='color: #555;'>Cod Depozit (Pal):</span> <br><span style='color: #28a745; font-weight: bold;'>{p_data['oracle_pal']}</span></div>
                <div><span style='color: #555;'>Cod Depozit (Box):</span> <br><span style='color: #28a745; font-weight: bold;'>{p_data['oracle_box']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pal_disp, cut_disp = get_available_stock_ui(real_prod)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Stoc PALEȚI", pal_disp)
        c2.metric("📦 Stoc BAXURI", cut_disp)
        c3.metric("🔄 Conversie WMS", f"{p_data['conversion']} bax/palet")
        c4.metric("⚖️ Conversie Fiscală", f"{p_data['conversie_baza']} {p_data['um_baza']}/bax")
        
        col_q1, col_q2, col_goala = st.columns([1, 1, 2])
        with col_q1: p_in = st.number_input("Paleți întregi:", min_value=0, step=1, key=f"p_{st.session_state.reset_counter}")
        with col_q2: b_in = st.number_input("Bax/Cutii (Fracție):", min_value=0, step=1, key=f"b_{st.session_state.reset_counter}")
        
        if st.button("➕ Adaugă în Listă"):
            if p_in == 0 and b_in == 0: st.warning("Pune o cantitate.")
            elif calculate_delta(real_prod, p_in, b_in):
                st.session_state.schita_comanda.append({
                    "Produs": real_prod, "Cod_NIR": p_data['cod_nir'], 
                    "Paleti": p_in, "Cutii": b_in, "Cod_Depozit_Pal": p_data['oracle_pal'],
                    "Cod_Depozit_Box": p_data['oracle_box'], "UM_Baza": p_data['um_baza'], "Conversie_Baza": p_data['conversie_baza']
                })
                force_reset(); st.rerun()
            else: st.error("❌ STOC INSUFICIENT!")
            
        st.divider()
        if len(st.session_state.schita_comanda) > 0:
            st.markdown("#### 🛒 Produse în comandă")
            for idx, item in enumerate(st.session_state.schita_comanda):
                colA, colB, colC = st.columns([3,2,1])
                colA.write(f"**{item['Produs']}**")
                colB.write(f"{item['Paleti']} Pal | {item['Cutii']} Bax")
                if colC.button("❌", key=f"del_{idx}"):
                    st.session_state.schita_comanda.pop(idx)
                    st.rerun()
            
            if st.button("👁️ Analizează (Auto-Convertor)", type="primary"):
                st.session_state.client_temporar_comandat = client
                st.session_state.mod_previzualizare = True
                st.rerun()
                
    else:
        st.markdown("### 🔍 Motor DIMO-NEXUS Activ")
        payload_log, payload_fisc = [], []
        for itm in st.session_state.schita_comanda:
            nume = itm['Produs']
            P, C, pal = st.session_state.db[nume]['conversion'], itm['Cutii'], itm['Paleti']
            if pal > 0: payload_log.append({"Acțiune / Cod Depozit": itm['Cod_Depozit_Pal'], "Cantitate": str(pal), "U.M. Logistic": "Palet"})
            if C > 0: payload_log.append({"Acțiune / Cod Depozit": itm['Cod_Depozit_Box'], "Cantitate": str(C), "U.M. Logistic": "Bax/Cutie"})
            tb = ((pal * P) + C) * itm['Conversie_Baza']
            payload_fisc.append({"Cod SB (NIR)": itm['Cod_NIR'], "Nomenclator Oficial": nume, "Cantitate (U.M.)": f"{tb} {itm['UM_Baza']}"})

        c1, c2 = st.columns(2)
        with c1: st.write("🚚 **Linii WMS**"); st.dataframe(pd.DataFrame(payload_log))
        with c2: st.write("🧾 **Linii Fiscale**"); st.dataframe(pd.DataFrame(payload_fisc))

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔙 Întoarce-te"): st.session_state.mod_previzualizare = False; st.rerun()
        with col_b2:
            if st.button("🚀 Trimite spre Depozit", type="primary"):
                st.session_state.istoric_comenzi_live.append({
                    "Comanda": st.session_state.order_number, "Client": st.session_state.client_temporar_comandat,
                    "Payload_Logistic": payload_log, "Payload_Fiscal": payload_fisc, "Status": "Asteapta Incarcare"
                })
                st.session_state.order_number += 1
                st.session_state.schita_comanda = []
                st.session_state.mod_previzualizare = False
                st.rerun()

with tab2:
    if len(st.session_state.istoric_comenzi_live) == 0:
        st.info("Nicio comandă nouă la rampă.")
    for idx, cmd in enumerate(st.session_state.istoric_comenzi_live):
        st.markdown(f"#### Comanda SCF-{cmd['Comanda']} | {cmd['Client']}")
        st.write(f"Status: **{cmd['Status']}**")
        
        if cmd['Status'] == "Asteapta Incarcare":
            if st.button("📲 Simulare WMS: Confirmare Încărcare", key=f"wms_{idx}"):
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Incarcat"
                st.rerun()
                
        elif cmd['Status'] == "Incarcat":
            if st.button("🖨️ EMITE ACTE (PDF + WMS)", type="primary", key=f"emit_{idx}"):
                generate_wms_csv(cmd['Comanda'], cmd['Payload_Logistic'])
                pdf_p = generate_pdf_aviz(cmd['Comanda'], cmd['Client'], cmd['Payload_Fiscal'])
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Documente Generate"
                st.session_state.istoric_comenzi_live[idx]['pdf_path'] = os.path.abspath(pdf_p)
                st.rerun()
                
        elif cmd['Status'] == "Documente Generate":
            st.success("✅ Actele sunt gata!")
            if os.path.exists(cmd['pdf_path']):
                # AICI E SECRETUL PT CLOUD: Afisare PDF în browser
                display_pdf(cmd['pdf_path'])
            
                with open(cmd['pdf_path'], "rb") as file:
                    st.download_button(
                        label="📥 Descarcă PDF-ul pentru a-l printa la EPSON",
                        data=file,
                        file_name=f"AVIZ_SCF_{cmd['Comanda']}.pdf",
                        mime="application/pdf"
                    )
        st.divider()
