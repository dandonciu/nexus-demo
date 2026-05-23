import streamlit as st
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import os
import csv
from fpdf import FPDF

# --- INITIALIZARE FOLDERE EXPORT ---
EXPORT_DIR = "exports"
PDF_DIR = os.path.join(EXPORT_DIR, "pdf_docs")
WMS_DIR = os.path.join(EXPORT_DIR, "wms_payloads")

for folder in [EXPORT_DIR, PDF_DIR, WMS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

st.set_page_config(page_title="NEXUS B2B", page_icon="📦", layout="wide")

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

# --- DB BUFFER (Baza de Lucru NEXUS) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "Prosoape V verzi": {
            "cod_nir": "NIR-209520", "oracle_pal": "PAL NV710", "oracle_box": "NV710",
            "stock_pal": 4, "stock_box": 15, "conversion": 32, # 32 cut/palet
            "um_baza": "Pachete", "conversie_baza": 20 # 20 pachete/cutie
        },
        "Role autocut albe TAD 220m": {
            "cod_nir": "NIR-156350", "oracle_pal": "PAL BKTp721", "oracle_box": "BKTp721",
            "stock_pal": 4, "stock_box": 32, "conversion": 48, # 48 bax/palet
            "um_baza": "Role", "conversie_baza": 6 # 6 role/bax
        },
        "Saci menaj 120L negri LDPE": {
            "cod_nir": "NIR-211125", "oracle_pal": "PAL IVFLX120LD-N", "oracle_box": "IVFLX120LD-N",
            "stock_pal": 5, "stock_box": 20, "conversion": 60, # estimat 60 bax/palet
            "um_baza": "Role", "conversie_baza": 15 # 15 role/bax
        }
    }

# Variables globale
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'order_number' not in st.session_state: st.session_state.order_number = 218395 # Nr din poza ta
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

# ================= MODULE GENERARE & PRINT =================
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
    pdf.set_font("Arial", 'B', 14)
    
    # Header - Split FURNIZOR / CLIENT
    c_data = clients_data[client_name]
    f_data = furnizor_data
    
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
    
    pdf.cell(90, 5, f"Banca: {f_data['Banca']}", ln=0)
    pdf.cell(10, 5, "", ln=0)
    pdf.cell(90, 5, f"Banca: {c_data['Banca']}", ln=1)
    
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
    pdf.cell(90, 5, "B.I./C.I.: ................................................", ln=1)
    pdf.cell(90, 5, "Mijloc auto nr: ........................................", ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 7)
    pdf.multi_cell(0, 4, clean_text("Prezentul document tine loc de Certificat de Origine si Calitate. Marfa ramane proprietatea Nova Safe SRL pana la achitarea integrala a contravalorii."))
    
    filepath = os.path.join(PDF_DIR, f"AVIZ_{order_no}.pdf")
    pdf.output(filepath)
    return filepath

def print_to_epson(filepath):
    try:
        os.startfile(filepath, "print")
        return True, "Success"
    except Exception as e:
        return False, str(e)


# ================= INTERFATA APP =================
if not st.session_state.logged_in:
    st.info("Logheaza-te cu parola: 'angajat'")
    pwd = st.text_input("Parola", type="password")
    if st.button("Log In"):
        if pwd == "angajat":
            st.session_state.logged_in, st.session_state.role = True, pwd
            st.rerun()
    st.stop()

st.title("⚡ NEXUS B2B - Rampa")
st.info(f"**Comanda Curenta:** SCF-{st.session_state.order_number}")

tab1, tab2 = st.tabs(["🛒 LANSARE DEPOZIT", "🖨️ EMITERE ACTE & PRINT"])

with tab1:
    if not st.session_state.mod_previzualizare:
        client = st.selectbox("Client", list(clients_data.keys()), key="cli")
        produse = list(st.session_state.db.keys()) + list(client_aliases.get(client, {}).keys())
        prod_sel = st.selectbox("Produs", produse, on_change=force_reset, key="prd")
        
        real_prod = client_aliases.get(client, {}).get(prod_sel, prod_sel)
        p_data = st.session_state.db[real_prod]
        
        pal_disp, cut_disp = get_available_stock_ui(real_prod)
        st.write(f"**Disponibil:** {pal_disp} paleti intregi | {cut_disp} cutii/baxuri libere")
        
        c1, c2 = st.columns(2)
        with c1: p_in = st.number_input("Paleti", min_value=0, key=f"p_{st.session_state.reset_counter}")
        with c2: b_in = st.number_input("Bax/Cutii", min_value=0, key=f"b_{st.session_state.reset_counter}")
        
        if st.button("Adauga in Cărucior"):
            if calculate_delta(real_prod, p_in, b_in):
                st.session_state.schita_comanda.append({
                    "Produs": real_prod, "Cod_NIR": p_data['cod_nir'], 
                    "Paleti": p_in, "Cutii": b_in, "Cod_Depozit_Pal": p_data['oracle_pal'],
                    "Cod_Depozit_Box": p_data['oracle_box'], "UM_Baza": p_data['um_baza'], "Conversie_Baza": p_data['conversie_baza']
                })
                force_reset()
                st.rerun()
            else: st.error("Stoc insuficient!")
            
        if len(st.session_state.schita_comanda) > 0:
            st.write(st.session_state.schita_comanda)
            if st.button("👁️ Analizeaza / Finalizeaza"):
                st.session_state.client_temporar_comandat = client
                st.session_state.mod_previzualizare = True
                st.rerun()
    else:
        st.warning("⚠️ Muta din BUFFER catre Depozit. Confirmare:")
        payload_log, payload_fisc = [], []
        
        for itm in st.session_state.schita_comanda:
            nume = itm['Produs']
            P, C, pal = st.session_state.db[nume]['conversion'], itm['Cutii'], itm['Paleti']
            
            # WMS (Formatul din poza ta)
            if pal > 0: payload_log.append({"Acțiune / Cod Depozit": itm['Cod_Depozit_Pal'], "Cantitate": str(pal), "U.M. Logistic": "Palet"})
            if C > 0: payload_log.append({"Acțiune / Cod Depozit": itm['Cod_Depozit_Box'], "Cantitate": str(C), "U.M. Logistic": "Bax/Cutie"})
            
            # Fiscal (SmartBill)
            tb = ((pal * P) + C) * itm['Conversie_Baza']
            payload_fisc.append({"Cod SB (NIR)": itm['Cod_NIR'], "Nomenclator Oficial": nume, "Cantitate (U.M.)": f"{tb} {itm['UM_Baza']}"})

        if st.button("🚀 Trimite la Depozit"):
            st.session_state.istoric_comenzi_live.append({
                "Comanda": st.session_state.order_number, "Client": st.session_state.client_temporar_comandat,
                "Payload_Logistic": payload_log, "Payload_Fiscal": payload_fisc, "Status": "Asteapta la Rampa"
            })
            st.session_state.order_number += 1
            st.session_state.schita_comanda = []
            st.session_state.mod_previzualizare = False
            st.rerun()

with tab2:
    for idx, cmd in enumerate(st.session_state.istoric_comenzi_live):
        st.write(f"### Comanda SCF-{cmd['Comanda']} | {cmd['Client']}")
        st.write(f"Status: **{cmd['Status']}**")
        
        if cmd['Status'] == "Asteapta la Rampa":
            if st.button("📲 Simulare WMS: Marfa a fost adusa de stivuitorist", key=f"wms_{idx}"):
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Operated"
                st.rerun()
                
        elif cmd['Status'] == "Operated":
            if st.button("🖨️ EMITE PDF & WMS", key=f"emit_{idx}"):
                csv_p = generate_wms_csv(cmd['Comanda'], cmd['Payload_Logistic'])
                pdf_p = generate_pdf_aviz(cmd['Comanda'], cmd['Client'], cmd['Payload_Fiscal'])
                st.session_state.istoric_comenzi_live[idx]['Status'] = "Documente Generate"
                st.session_state.istoric_comenzi_live[idx]['pdf_path'] = os.path.abspath(pdf_p)
                st.rerun()
                
        elif cmd['Status'] == "Documente Generate":
            st.success("Fisierele s-au creat in folderul /exports/!")
            if st.button("📠 PRINTEAZA FIZIC LA EPSON", type="primary", key=f"prt_{idx}"):
                succes, err = print_to_epson(cmd['pdf_path'])
                if succes: st.balloons(); st.success("✅ COMANDA DE PRINT A FOST TRIMISA LA WINDOWS!")
                else: st.error(f"Eroare Windows Print: {err}")
        st.divider()
