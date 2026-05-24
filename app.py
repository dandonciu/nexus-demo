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

# --- BANNER ---
st.markdown("""
    <div style="background: linear-gradient(90deg, #003366 0%, #004080 100%); padding: 20px 30px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; color: white; margin-bottom: 25px;">
        <div>
            <h1 style="margin: 0; padding: 0; color: #ffffff; font-size: 2.5rem; letter-spacing: 1px;">📦 NEXUS</h1>
            <p style="margin: 0; padding: 0; font-style: italic; color: #a8c5e8; font-size: 1.1rem; margin-top: -5px;">Rezolva probleme, nu le creeaza.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; padding: 0; font-weight: bold; font-size: 1.3rem;">NOVA SAFE SRL</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DATE REALE ---
furnizor_data = {
    "Nume": "NOVA SAFE SRL", "RegCom": "J2015015825407", "CIF": "RO35368260",
    "Adresa": "Str. Turturelelor 11B, Bucuresti", "Banca": "Banca Transilvania", "IBAN": "RO72BTRLRONCRT0363372001"
}

clients_data = {
    "S.C. SIDE GRUP S.R.L.": {"RegCom": "J2003000200023", "CIF": "RO15216895", "Adresa": "Felnac, Nr.1000, judet Arad", "Banca": "UNICREDIT BANK", "IBAN": "RO20 BACX 0066 4409"},
    "DSCM TECH SRL": {"RegCom": "J17/1179/2013", "CIF": "RO32278456", "Adresa": "Com T.Vladimirescu 993, Galati", "Banca": "Raiffeisen Bank", "IBAN": "-"}
}

client_aliases = {
    "S.C. SIDE GRUP S.R.L.": {"Prosoape Verzi Pliate": "Prosoape V verzi"},
    "DSCM TECH SRL": {"Role Albe Stergere": "Role autocut albe TAD 220m"}
}

# --- DB BUFFER ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "Prosoape V verzi": {"cod_nir": "NIR-209520", "oracle_pal": "PAL NV710", "oracle_box": "NV710", "stock_pal": 4, "stock_box": 15, "conversion": 32, "um_baza": "Pachete", "conversie_baza": 20},
        "Role autocut albe TAD 220m": {"cod_nir": "NIR-156350", "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721", "stock_pal": 4, "stock_box": 32, "conversion": 48, "um_baza": "Role", "conversie_baza": 6},
        "Saci menaj 120L negri LDPE": {"cod_nir": "NIR-211125", "oracle_pal": "PAL IVFLX120LD-N", "oracle_box": "IVFLX120LD-N", "stock_pal": 5, "stock_box": 20, "conversion": 60, "um_baza": "Role", "conversie_baza": 15}
    }

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'order_number' not in st.session_state: st.session_state.order_number = 218395
if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
if 'schita_comanda' not in st.session_state: st.session_state.schita_comanda = []
if 'mod_previzualizare' not in st.session_state: st.session_state.mod_previzualizare = False
if 'istoric_comenzi_live' not in st.session_state: st.session_state.istoric_comenzi_live = []

def clean_text(txt):
    replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
    for k, v in replacements.items(): txt = str(txt).replace(k, v)
    return txt

# ================= MOTOR GENERARE MULTI-PAGE PDF =================
def generate_pdf_document(order_no, client_name, payload_fiscal):
    pdf = FPDF()
    c_data = clients_data[client_name]
    f_data = furnizor_data
    
    # === PAGINA 1: AVIZ DE INSOTIRE (Piatra din Rosetta) ===
    pdf.add_page()
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 5, clean_text(f"FURNIZOR: {f_data['Nume']}"), ln=0); pdf.cell(10, 5, "", ln=0); pdf.cell(90, 5, clean_text(f"CUMPARATOR: {client_name}"), ln=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(90, 4, f"CIF: {f_data['CIF']} | J: {f_data['RegCom']}", ln=0); pdf.cell(10, 4, "", ln=0); pdf.cell(90, 4, f"CIF: {c_data['CIF']} | J: {c_data['RegCom']}", ln=1)
    pdf.cell(90, 4, clean_text(f"Sediul: {f_data['Adresa']}"), ln=0); pdf.cell(10, 4, "", ln=0); pdf.cell(90, 4, clean_text(f"Sediul: {c_data['Adresa']}"), ln=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "AVIZ DE INSOTIRE A MARFII", align='C', ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"Seria NEXUS Nr. {order_no} | Data: {datetime.now().strftime('%d.%m.%Y')}", align='C', ln=1)
    pdf.ln(5)
    
    # Tabel Aviz (Cu WMS si NIR)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(8, 8, "Nr", 1, 0, 'C')
    pdf.cell(25, 8, "Cod WMS", 1, 0, 'C')
    pdf.cell(25, 8, "Cod NIR", 1, 0, 'C')
    pdf.cell(85, 8, "Specificatia (Denumire)", 1, 0, 'C')
    pdf.cell(15, 8, "U.M.", 1, 0, 'C')
    pdf.cell(30, 8, "Cantitate", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    for i, item in enumerate(payload_fiscal):
        pdf.cell(8, 7, str(i+1), 1, 0, 'C')
        pdf.cell(25, 7, str(item.get('Cod_Depozit', '-')), 1, 0, 'C')
        pdf.cell(25, 7, str(item.get('Cod SB (NIR)', '-')), 1, 0, 'C')
        pdf.cell(85, 7, clean_text(item['Nomenclator Oficial'][:50]), 1, 0)
        u_m = item['Cantitate (U.M.)'].split(' ')[1]
        qty = item['Cantitate (U.M.)'].split(' ')[0]
        pdf.cell(15, 7, u_m, 1, 0, 'C')
        pdf.cell(30, 7, qty, 1, 1, 'C')
        
    pdf.ln(20)
    pdf.cell(0, 5, "Semnatura si stampila furnizorului .........................       Semnatura de primire .........................", ln=1)
    
    # === PAGINA 2: DISPOZITIE DE LIVRARE ===
    pdf.add_page()
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, clean_text(f"Furnizor: {f_data['Nume']}"), ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "DISPOZITIE DE LIVRARE", align='C', ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"Nr. {order_no} / Data: {datetime.now().strftime('%d.%m.%Y')}", align='C', ln=1)
    pdf.ln(5)
    pdf.cell(0, 5, clean_text(f"Veti elibera produsele de mai jos catre {client_name} prin delegatul ................................................."), ln=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 8, "Nr", 1, 0, 'C')
    pdf.cell(100, 8, "Denumirea produselor", 1, 0, 'C')
    pdf.cell(20, 8, "U/M", 1, 0, 'C')
    pdf.cell(30, 8, "Cant. Dispusa", 1, 0, 'C')
    pdf.cell(30, 8, "Cant. Livrata", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
    for i, item in enumerate(payload_fiscal):
        pdf.cell(10, 7, str(i+1), 1, 0, 'C')
        pdf.cell(100, 7, clean_text(item['Nomenclator Oficial'][:50]), 1, 0)
        pdf.cell(20, 7, item['Cantitate (U.M.)'].split(' ')[1], 1, 0, 'C')
        pdf.cell(30, 7, item['Cantitate (U.M.)'].split(' ')[0], 1, 0, 'C')
        pdf.cell(30, 7, "", 1, 1, 'C') # Spatiu pt completare manuala WMS
        
    pdf.ln(15)
    pdf.cell(0, 5, "Dispus livrarea ....................      Gestionar ....................      Primitor ....................", ln=1)

    # === PAGINA 3: DECLARATIE DE CONFORMITATE ===
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 6, clean_text(f"{f_data['Nume']}"), ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, clean_text(f"Adresa: {f_data['Adresa']}"), ln=1)
    pdf.cell(0, 5, f"RC: {f_data['RegCom']} | CUI: {f_data['CIF']}", ln=1)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "DECLARATIE DE CONFORMITATE", align='C', ln=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 10)
    text_decl = f"Noi, {f_data['Nume']}, cu sediul in {clean_text(f_data['Adresa'])}, inregistrata cu {f_data['RegCom']}, asiguram, garantam si declaram pe propria raspundere, conform prevederilor art. 5 din HG nr. 1.022/2002 privind regimul produselor si serviciilor care pot pune in pericol viata, sanatatea, securitatea muncii si protectia mediului, ca produsele enumerate mai jos, livrate cu Avizul Nr. {order_no}/{datetime.now().strftime('%d.%m.%Y')}, nu pun in pericol viata, sanatatea, securitatea muncii, nu produc un impact negativ asupra mediului si sunt conforme cu specificatiile din documentatia tehnica."
    pdf.multi_cell(0, 6, clean_text(text_decl))
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    for item in payload_fiscal:
        pdf.cell(0, 6, clean_text(f"- {item['Nomenclator Oficial']}"), ln=1)
        
    pdf.ln(20)
    pdf.cell(0, 6, "Manager,", ln=1)
    pdf.cell(0, 6, "Dan Donciu", ln=1)

    filepath = os.path.join(PDF_DIR, f"DOCUMENTE_NEXUS_{order_no}.pdf")
    pdf.output(filepath)
    return filepath

def display_pdf(file_path):
    with open(file_path, "rb") as f: base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ================= INTERFATA =================
if not st.session_state.logged_in:
    st.info("Parola: angajat")
    pwd = st.text_input("Parola", type="password")
    if st.button("Log In"):
        if pwd == "angajat": st.session_state.logged_in = True; st.rerun()
    st.stop()

st.title("⚡ NEXUS - Lansare Rampa")
tab1, tab2 = st.tabs(["🛒 Schiță Comandă", "🚚 Rampa & Acte (3-in-1)"])

with tab1:
    if not st.session_state.mod_previzualizare:
        client = st.selectbox("Client", list(clients_data.keys()))
        produse = list(st.session_state.db.keys()) + list(client_aliases.get(client, {}).keys())
        prod_sel = st.selectbox("Produs", produse, on_change=lambda: st.session_state.update({"reset_counter": st.session_state.reset_counter + 1}))
        
        real_prod = client_aliases.get(client, {}).get(prod_sel, prod_sel)
        p_data = st.session_state.db[real_prod]
        
        c1, c2 = st.columns(2)
        p_in = c1.number_input("Paleți întregi:", min_value=0, key=f"p_{st.session_state.reset_counter}")
        b_in = c2.number_input("Bax/Cutii (Fracție):", min_value=0, key=f"b_{st.session_state.reset_counter}")
        
        if st.button("➕ Adaugă in Cărucior"):
            if p_in > 0 or b_in > 0:
                st.session_state.schita_comanda.append({
                    "Produs": real_prod, "Cod_NIR": p_data['cod_nir'], "Cod_Depozit": p_data['oracle_box'],
                    "Paleti": p_in, "Cutii": b_in, "UM_Baza": p_data['um_baza'], "Conversie_Baza": p_data['conversie_baza']
                })
                st.session_state.reset_counter += 1
                st.rerun()
                
        if len(st.session_state.schita_comanda) > 0:
            st.write(st.session_state.schita_comanda)
            if st.button("👁️ Trimite la Rampa"):
                st.session_state.client_temporar_comandat = client
                st.session_state.mod_previzualizare = True
                st.rerun()
                
    else:
        st.warning("Confirmare Lansare WMS")
        payload_fisc = []
        for itm in st.session_state.schita_comanda:
            nume = itm['Produs']
            P, C, pal = st.session_state.db[nume]['conversion'], itm['Cutii'], itm['Paleti']
            tb = ((pal * P) + C) * itm['Conversie_Baza']
            payload_fisc.append({
                "Cod_Depozit": itm['Cod_Depozit'], "Cod SB (NIR)": itm['Cod_NIR'], 
                "Nomenclator Oficial": nume, "Cantitate (U.M.)": f"{tb} {itm['UM_Baza']}"
            })

        if st.button("🚀 CONFIRMA SI TRIMITE"):
            st.session_state.istoric_comenzi_live.append({
                "Comanda": st.session_state.order_number, "Client": st.session_state.client_temporar_comandat,
                "Payload_Fiscal": payload_fisc, "Status": "Asteapta Incarcare"
            })
            st.session_state.order_number += 1
            st.session_state.schita_comanda.clear() # BARIERA PT ZERO QUANTITY BUG
            st.session_state.mod_previzualizare = False
            st.rerun()

with tab2:
    for idx, cmd in enumerate(st.session_state.istoric_comenzi_live):
        st.info(f"Cmd {cmd['Comanda']} | {cmd['Client']} | Status: {cmd['Status']}")
        
        if cmd['Status'] == "Asteapta Incarcare":
            if st.button("Confirmat Incarcare", key=f"inc_{idx}"):
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Incarcat"
                st.rerun()
                
        elif cmd['Status'] == "Incarcat":
            if st.button("🖨️ EMITE SET ACTE (Aviz + Disp + Decl)", type="primary", key=f"emit_{idx}"):
                pdf_p = generate_pdf_document(cmd['Comanda'], cmd['Client'], cmd['Payload_Fiscal'])
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Documente Generate"
                st.session_state.istoric_comenzi_live[idx]['pdf_path'] = pdf_p
                st.rerun()
                
        elif cmd['Status'] == "Documente Generate":
            display_pdf(cmd['pdf_path'])
            with open(cmd['pdf_path'], "rb") as file:
                st.download_button("📥 Descarca Setul Complet (PDF)", data=file, file_name=f"Set_Acte_{cmd['Comanda']}.pdf", mime="application/pdf")
