import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import base64
from fpdf import FPDF

# Importăm datele din DB-ul nostru
from backend.database.clients_config import clients_data, furnizor_data, client_aliases

import tempfile
# Setări foldere PDF (Compatibil cu Streamlit Cloud)
PDF_DIR = tempfile.gettempdir()

# --- FUNCTII UTILE ---
def force_reset(): st.session_state.reset_counter += 1

def clean_text(txt):
    replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
    for k, v in replacements.items(): txt = str(txt).replace(k, v)
    return txt

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
    total_dorit = (cmd_pal * st.session_state.db[prod_key]['conversion']) + cmd_box
    deja_in_cos = sum([(i['Paleti'] * st.session_state.db[prod_key]['conversion']) + i['Cutii'] for i in st.session_state.schita_comanda if i['Produs'] == prod_key])
    return (total_dorit + deja_in_cos) <= get_total_boxes(prod_key)

# ==========================================
# --- MOTOR PDF (FĂRĂ PREȚURI, LEGAL 100%) ---
# ==========================================
def generate_pdf_document(order_no, client_name, payload_fiscal, payload_log):
    pdf = FPDF()
    c_data = clients_data[client_name]
    f_data = furnizor_data
    data_azi = datetime.now().strftime('%d/%m/%Y')
    
    # ---------------------------------------------------------
    # PAGINA 1: AVIZ DE INSOTIRE (FĂRĂ VALORI FINANCIARE)
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "AVIZ DE INSOTIRE A MARFII", align='C', ln=1)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Seria NS nr. {order_no} | Data: {data_azi}", align='C', ln=1)
    pdf.ln(5)
    
    # Date Furnizor & Client
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(95, 5, clean_text(f"Furnizor: {f_data['Nume']}"), ln=0); pdf.cell(95, 5, clean_text(f"Client: {client_name}"), ln=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(95, 4, f"CIF: {f_data['CIF']} | J: {f_data['RegCom']}", ln=0); pdf.cell(95, 4, f"CIF: {c_data['CIF']} | J: {c_data['RegCom']}", ln=1)
    pdf.cell(95, 4, clean_text(f"Adresa: {f_data['Adresa']}"), ln=0); pdf.cell(95, 4, clean_text(f"Adresa: {c_data['Adresa']}"), ln=1)
    pdf.ln(5)
    
    # Tabel Nou - Doar Cantitativ (Lățime totală 190)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(10, 8, "Nr.", 1, 0, 'C')
    pdf.cell(130, 8, "Denumirea produselor", 1, 0, 'C')
    pdf.cell(20, 8, "U.M.", 1, 0, 'C')
    pdf.cell(30, 8, "Cantitate", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    for i, item in enumerate(payload_fiscal):
        cantitate_neta = float(item['Cantitate (U.M.)'].split(' ')[0])
        cod_nc = "48236990" 
        
        # Rândul 1 (Denumire Produs)
        pdf.cell(10, 5, str(i+1), 'L,T,R', 0, 'C')
        pdf.cell(130, 5, clean_text(f"({item.get('Cod_Depozit', '-')}) {item['Nomenclator Oficial'][:75]}"), 'L,T,R', 0, 'L')
        pdf.cell(20, 5, clean_text(item['Cantitate (U.M.)'].split(' ')[1]), 'L,T,R', 0, 'C')
        pdf.cell(30, 5, str(cantitate_neta), 'L,T,R', 1, 'C')
        
        # Rândul 2 (Cod NC)
        pdf.cell(10, 4, "", 'L,B,R', 0, 'C')
        pdf.set_text_color(100, 100, 100) # Gri
        pdf.cell(130, 4, f"Cod NC: {cod_nc}", 'L,B,R', 0, 'L')
        pdf.set_text_color(0, 0, 0)
        pdf.cell(20, 4, "", 'L,B,R', 0, 'C')
        pdf.cell(30, 4, "", 'L,B,R', 1, 'C')

    # Rânduri goale
    for _ in range(2):
        pdf.cell(10, 6, "", 1, 0); pdf.cell(130, 6, "", 1, 0); pdf.cell(20, 6, "", 1, 0); pdf.cell(30, 6, "", 1, 1)

    # Sub-Tabel (Comanda Achiziție)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(190, 6, f"Nr. comanda achizitie: AR {order_no}/{data_azi.split('/')[2]}", 'L,T,R', 1, 'L')
    pdf.set_font("Arial", '', 8)
    pdf.cell(190, 6, f"AR {order_no} (Comanda {client_name})", 'L,B,R', 1, 'L')
    
    # Subsol (Date de expediție conform Legii)
    pdf.ln(5)
    pdf.set_font("Arial", '', 8)
    pdf.cell(95, 5, "Semnatura si stampila furnizorului:", 'L,T,R', 0, 'L')
    pdf.cell(95, 5, "Date privind expeditia:", 'L,T,R', 1, 'L')
    
    pdf.cell(95, 5, "", 'L,R', 0, 'L')
    pdf.cell(95, 5, "Numele delegatului: .....................................................", 'L,R', 1, 'L')
    
    pdf.cell(95, 5, "", 'L,R', 0, 'L')
    pdf.cell(95, 5, "B.I./C.I. seria: ....... nr. ............................", 'L,R', 1, 'L')
    
    pdf.cell(95, 5, "Intocmit de: NEXUS Auto-Sistem", 'L,R', 0, 'L')
    pdf.cell(95, 5, "Mijloc de transport: ................................. nr: ..................", 'L,R', 1, 'L')
    
    pdf.cell(95, 5, "", 'L,B,R', 0, 'L')
    pdf.cell(95, 5, f"Expedierea s-a facut in prezenta noastra la data: {data_azi}", 'L,B,R', 1, 'L')

    # ---------------------------------------------------------
    # PAGINA 2: DISPOZITIE DEPOZIT (WMS CLAR)
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 8, "DISPOZITIE DE LIVRARE (COMANDA DEPOZIT)", align='C', ln=1)
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, f"Nr. {order_no} / Data: {data_azi}", align='C', ln=1); pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(15, 8, "Nr", 1, 0, 'C'); pdf.cell(40, 8, "Cod Gestiune (Raft)", 1, 0, 'C')
    pdf.cell(85, 8, "Denumirea Produsului", 1, 0, 'C'); pdf.cell(25, 8, "Cantitate", 1, 0, 'C'); pdf.cell(25, 8, "Tip (U/M)", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
    for i, item in enumerate(payload_log):
        is_palet = "PAL" in item['UM'].upper()
        pdf.cell(15, 8, str(i+1), 1, 0, 'C')
        if is_palet:
            pdf.set_font("Arial", 'B', 9); pdf.cell(40, 8, str(item.get('Cod Gestiune', '-')), 1, 0, 'C'); pdf.set_font("Arial", '', 9)
        else:
            pdf.cell(40, 8, str(item.get('Cod Gestiune', '-')), 1, 0, 'C')
            
        pdf.cell(85, 8, clean_text(item['Denumire'][:50]), 1, 0)
        pdf.cell(25, 8, str(item['Cant']), 1, 0, 'C')
        if is_palet:
            pdf.set_fill_color(220, 220, 220); pdf.cell(25, 8, "PALET", 1, 1, 'C', fill=True)
        else:
            pdf.cell(25, 8, "CUTIE/BAX", 1, 1, 'C')

    pdf.ln(20)
    pdf.cell(0, 5, "Dispus livrarea ....................      Gestionar ....................      Primitor ....................", ln=1)

    # ---------------------------------------------------------
    # PAGINA 3: DECLARATIE DE CONFORMITATE
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "DECLARATIE DE CONFORMITATE", align='C', ln=1); pdf.ln(10)
    pdf.set_font("Arial", '', 11)
    decl_text = f"Subscrisa {f_data['Nume']}, cu sediul in {f_data['Adresa']}, declaram pe propria raspundere ca produsele livrate cu Avizul Nr. {order_no}/{data_azi} respecta normele de calitate si siguranta in vigoare."
    pdf.multi_cell(0, 7, clean_text(decl_text)); pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    for item in payload_fiscal: pdf.cell(0, 6, clean_text(f"- {item['Nomenclator Oficial']}"), ln=1)
    pdf.ln(30); pdf.cell(0, 6, "Semnatura Manager / Calitate,", ln=1)

    filepath = os.path.join(PDF_DIR, f"DOCUMENTE_NEXUS_{order_no}.pdf")
    pdf.output(filepath)
    return filepath

def display_pdf(file_path):
    with open(file_path, "rb") as f: base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>', unsafe_allow_html=True)

# ==========================================
# --- FUNCTIA PRINCIPALA A MODULULUI ---
# ==========================================
def render_lansare_module():
    if 'order_number' not in st.session_state: st.session_state.order_number = 218395
    if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
    if 'schita_comanda' not in st.session_state: st.session_state.schita_comanda = []
    if 'mod_previzualizare' not in st.session_state: st.session_state.mod_previzualizare = False
    if 'istoric_comenzi_live' not in st.session_state: st.session_state.istoric_comenzi_live = []

    st.title("📦 NEXUS Lansare Comenzi")
    tab1, tab2 = st.tabs(["🛒 Formare Comandă", "🚚 Gestiune Rampă & Acte"])
    
    with tab1:
        if not st.session_state.mod_previzualizare:
            client_ales = st.selectbox("Client", list(clients_data.keys()))
            baza_produse = list(st.session_state.db.keys())
            aliasuri_client_curent = client_aliases.get(client_ales, {})
            produse_disponibile = baza_produse + list(aliasuri_client_curent.keys())
            
            selected_option = st.selectbox("Produs", produse_disponibile, on_change=force_reset, key="select_prod")
            
            if selected_option in aliasuri_client_curent:
                prod_name = aliasuri_client_curent[selected_option]
                alias_folosit = selected_option
                st.success(f"🔄 Alias recunoscut: **{selected_option}** = **{prod_name}**")
            else:
                prod_name = selected_option
                alias_folosit = None

            p_data = st.session_state.db[prod_name]
            av_pal, av_box = get_available_stock_ui(prod_name)
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("📦 Stoc PALEȚI", av_pal)
            col_s2.metric("📦 Stoc CUTII", av_box)
            col_s3.metric("🔄 Conversie WMS", f"{p_data['conversion']} cutii/pal")
            col_s4.metric("⚖️ Conversie Fiscală", f"{p_data['conversie_baza']} {p_data['um_baza']}/cutie")
            
            col_q1, col_q2, col_goala = st.columns([1, 1, 2])
            with col_q1: order_pal = st.number_input("Nr. PALEȚI:", min_value=0, step=1, key=f'input_pal_{st.session_state.reset_counter}')
            with col_q2: order_box = st.number_input("Nr. CUTII (fracție):", min_value=0, step=1, key=f'input_box_{st.session_state.reset_counter}')
            
            if st.button("➕ Adaugă în Listă"):
                if order_pal == 0 and order_box == 0:
                    st.warning("Introduceți o cantitate.")
                elif not calculate_delta(prod_name, order_pal, order_box):
                    st.error("❌ STOC INSUFICIENT!")
                else:
                    st.session_state.schita_comanda.append({
                        "Produs": prod_name, "Cod_NIR": p_data['cod_nir'], "Alias_Folosit": alias_folosit,
                        "Paleti": order_pal, "Cutii": order_box, "Cod_Depozit_Pal": p_data['oracle_pal'],
                        "Cod_Depozit_Box": p_data['oracle_box'], "UM_Baza": p_data['um_baza'], "Conversie_Baza": p_data['conversie_baza']
                    })
                    force_reset(); st.rerun()

            st.divider()

            if len(st.session_state.schita_comanda) > 0:
                st.markdown(f"#### 🛒 Produse în comandă (Către: **{client_ales}**)")
                h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
                h1.markdown("**Produs**"); h2.markdown("**Cod WMS**"); h3.markdown("**Cantitate**"); h4.markdown("**Total Fiscal**"); h5.markdown("**Sterge**")
                st.markdown("<hr style='margin-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                
                for idx, item in enumerate(st.session_state.schita_comanda):
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                    nume = item['Produs'] + (f" <br><span style='color: #e67e22; font-size:0.85rem;'>(Ref: {item['Alias_Folosit']})</span>" if item.get('Alias_Folosit') else "")
                    c1.markdown(nume, unsafe_allow_html=True)
                    c2.markdown(f"{item['Cod_Depozit_Pal']} / {item['Cod_Depozit_Box']}")
                    c3.markdown(f"**{item['Paleti']}** Pal | **{item['Cutii']}** Cut")
                    c4.markdown(f"**{((item['Paleti'] * st.session_state.db[item['Produs']]['conversion']) + item['Cutii']) * item['Conversie_Baza']}** {item['UM_Baza']}")
                    if c5.button("❌", key=f"del_row_{idx}"): st.session_state.schita_comanda.pop(idx); st.rerun()
                
                st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns([1, 3])
                with c_btn1:
                    if st.button("🗑️ Golește Lista"): st.session_state.schita_comanda = []; st.rerun()
                with c_btn2:
                    if st.button("👁️ Analizează Scindarea Dimo-NEXUS", type="primary", use_container_width=True):
                        st.session_state.client_temporar_comandat = client_ales
                        st.session_state.mod_previzualizare = True; st.rerun()

        # ECRAN B: PREVIZUALIZARE
        else:
            client_ales_prev = st.session_state.client_temporar_comandat
            st.markdown("### 🔍 Previzualizare: Dimo-NEXUS")
            
            payload_logistic_curent = []; payload_fiscal_curent = []
            
            for item in st.session_state.schita_comanda:
                nume_oficial = item['Produs']
                P = st.session_state.db[nume_oficial]['conversion']; L = st.session_state.db[nume_oficial]['stock_box']
                C = item['Cutii']; pallets_ordered = item['Paleti']
                
                if C > 0:
                    if (P - C) < C and L < C:
                        if pallets_ordered > 0: payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})
                        payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Denumire": f"{nume_oficial} (EXTRAGE {P - C} cutii)", "Cant": "1", "UM": "PAL"})
                    else:
                        if pallets_ordered > 0: payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})
                        if C <= L: payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Denumire": f"{nume_oficial} (Din stoc liber)", "Cant": str(C), "UM": "Cutii"})
                        else:
                            if L > 0: payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Denumire": f"{nume_oficial} (Goleste liber)", "Cant": str(L), "UM": "Cutii"})
                            payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Denumire": f"{nume_oficial} (Din palet nou)", "Cant": str(C - L), "UM": "Cutii"})
                else:
                    if pallets_ordered > 0: payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})

                total_cutii = (pallets_ordered * P) + C
                payload_fiscal_curent.append({
                    "Cod_Depozit": item['Cod_Depozit_Pal'], "Nomenclator Oficial": nume_oficial, "Cantitate (U.M.)": f"{total_cutii * item['Conversie_Baza']} {item['UM_Baza']}"
                })

            c_prism1, c_prism2 = st.columns(2)
            with c_prism1: st.warning("#### 🚚 Spre Stivuitorist (Logistic)"); st.dataframe(pd.DataFrame(payload_logistic_curent)[['Cod Gestiune', 'Denumire', 'Cant', 'UM']], hide_index=True)
            with c_prism2: st.success("#### 🧾 Spre SmartBill (Fiscal)"); st.dataframe(pd.DataFrame(payload_fiscal_curent)[['Cod_Depozit', 'Nomenclator Oficial', 'Cantitate (U.M.)']], hide_index=True)
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("🔙 Întoarce-te"): st.session_state.mod_previzualizare = False; st.rerun()
            with cb2:
                if st.button("🚀 LANSEAZĂ LA RAMPĂ", type="primary", use_container_width=True):
                    for item in st.session_state.schita_comanda:
                        prod = item['Produs']; P = st.session_state.db[prod]['conversion']; C = item['Cutii']; pallets_ordered = item['Paleti']
                        stoc_curent = get_total_boxes(prod)
                        stoc_ramas = stoc_curent - ((pallets_ordered * P) + C)
                        st.session_state.db[prod]['stock_pal'] = stoc_ramas // P; st.session_state.db[prod]['stock_box'] = stoc_ramas % P
                    st.session_state.istoric_comenzi_live.append({"Comanda": st.session_state.order_number, "Client": client_ales_prev, "Payload_Logistic": payload_logistic_curent, "Payload_Fiscal": payload_fiscal_curent, "Status": "Asteapta Incarcare"})
                    st.session_state.order_number += 1; st.session_state.schita_comanda = []; st.session_state.mod_previzualizare = False; st.rerun()

    with tab2:
        st.markdown("### 🚚 Emiteri Acte PDF")
        if len(st.session_state.istoric_comenzi_live) == 0: st.info("Nicio comandă la rampă.")
        for idx, cmd in enumerate(st.session_state.istoric_comenzi_live):
            st.write(f"**Cmd NEXUS-{cmd['Comanda']} | {cmd['Client']}** -> Status: {cmd['Status']}")
            if cmd['Status'] == "Asteapta Incarcare":
                if st.button("✅ Confirmare Încărcare", key=f"inc_{idx}"): st.session_state.istoric_comenzi_live[idx]['Status'] = "Incarcat"; st.rerun()
            elif cmd['Status'] == "Incarcat":
                if st.button("🖨️ EMITE ACTE", type="primary", key=f"emit_{idx}"):
                    pdf_p = generate_pdf_document(cmd['Comanda'], cmd['Client'], cmd['Payload_Fiscal'], cmd['Payload_Logistic'])
                    st.session_state.istoric_comenzi_live[idx]['Status'] = "Documente Generate"; st.session_state.istoric_comenzi_live[idx]['pdf_path'] = pdf_p; st.rerun()
            elif cmd['Status'] == "Documente Generate":
                display_pdf(cmd['pdf_path'])
                with open(cmd['pdf_path'], "rb") as file: st.download_button("📥 Descarcă", data=file, file_name=f"Aviz_{cmd['Comanda']}.pdf", mime="application/pdf")
            st.divider()
