import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64
from fpdf import FPDF

# Importăm datele din DB-ul nostru proaspăt creat
from backend.database.clients_config import clients_data, furnizor_data, client_aliases

# Setări foldere PDF
EXPORT_DIR = "exports"
PDF_DIR = os.path.join(EXPORT_DIR, "pdf_docs")
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

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

# --- MOTOR PDF REPARAT ---
def generate_pdf_document(order_no, client_name, payload_fiscal, payload_log):
    pdf = FPDF()
    c_data = clients_data[client_name]
    f_data = furnizor_data
    data_azi = datetime.now().strftime('%d.%m.%Y')
    
    # PAGINA 1: FISCAL
    pdf.add_page()
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 5, clean_text(f"FURNIZOR: {f_data['Nume']}"), ln=0); pdf.cell(10, 5, "", ln=0); pdf.cell(90, 5, clean_text(f"CUMPARATOR: {client_name}"), ln=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(90, 4, f"CIF: {f_data['CIF']} | J: {f_data['RegCom']}", ln=0); pdf.cell(10, 4, "", ln=0); pdf.cell(90, 4, f"CIF: {c_data['CIF']} | J: {c_data['RegCom']}", ln=1)
    pdf.cell(90, 4, clean_text(f"Sediul: {f_data['Adresa']}"), ln=0); pdf.cell(10, 4, "", ln=0); pdf.cell(90, 4, clean_text(f"Sediul: {c_data['Adresa']}"), ln=1)
    pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 8, "AVIZ DE INSOTIRE A MARFII", align='C', ln=1)
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, f"Seria NEXUS Nr. {order_no} | Data: {data_azi}", align='C', ln=1); pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(8, 8, "Nr", 1, 0, 'C'); pdf.cell(25, 8, "Cod Depozit", 1, 0, 'C'); pdf.cell(25, 8, "Cod NIR", 1, 0, 'C')
    pdf.cell(85, 8, "Specificatia (Denumire)", 1, 0, 'C'); pdf.cell(15, 8, "U.M.", 1, 0, 'C'); pdf.cell(30, 8, "Cantitate", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    for i, item in enumerate(payload_fiscal):
        pdf.cell(8, 7, str(i+1), 1, 0, 'C')
        pdf.cell(25, 7, str(item.get('Cod_Depozit', '-')), 1, 0, 'C')
        pdf.cell(25, 7, str(item.get('Cod SB (NIR)', '-')), 1, 0, 'C')
        pdf.cell(85, 7, clean_text(item['Nomenclator Oficial'][:50]), 1, 0)
        pdf.cell(15, 7, clean_text(item['Cantitate (U.M.)'].split(' ')[1]), 1, 0, 'C')
        pdf.cell(30, 7, clean_text(item['Cantitate (U.M.)'].split(' ')[0]), 1, 1, 'C')
    
    pdf.ln(15)
    pdf.cell(0, 5, "Semnatura si stampila furnizorului .........................       Semnatura de primire .........................", ln=1)
    
    # PAGINA 2: DISPOZITIE WMS
    pdf.add_page()
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, clean_text(f"Furnizor: {f_data['Nume']}"), ln=1); pdf.ln(5)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 8, "DISPOZITIE DE LIVRARE (COMANDA DEPOZIT)", align='C', ln=1)
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, f"Nr. {order_no} / Data: {data_azi}", align='C', ln=1); pdf.ln(5)
    pdf.cell(0, 5, clean_text(f"Veti elibera produsele de mai jos catre {client_name} prin delegatul ................................................."), ln=1); pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(8, 8, "Nr", 1, 0, 'C'); pdf.cell(22, 8, "Cod Gestiune", 1, 0, 'C'); pdf.cell(22, 8, "Cod NIR", 1, 0, 'C')
    pdf.cell(78, 8, "Denumirea / Instructiune WMS", 1, 0, 'C'); pdf.cell(15, 8, "U/M", 1, 0, 'C')
    pdf.cell(22, 8, "Cant. Dispusa", 1, 0, 'C'); pdf.cell(23, 8, "Cant. Livrata", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    for i, item in enumerate(payload_log):
        pdf.cell(8, 7, str(i+1), 1, 0, 'C')
        pdf.cell(22, 7, str(item.get('Cod Gestiune', '-')), 1, 0, 'C')
        pdf.cell(22, 7, str(item.get('Cod SB (NIR)', '-')), 1, 0, 'C')
        pdf.cell(78, 7, clean_text(item['Denumire'][:55]), 1, 0)
        pdf.cell(15, 7, clean_text(item['UM']), 1, 0, 'C')
        pdf.cell(22, 7, str(item['Cant']), 1, 0, 'C')
        pdf.cell(23, 7, "", 1, 1, 'C')
        
    pdf.ln(15)
    pdf.cell(0, 5, "Dispus livrarea ....................      Gestionar ....................      Primitor ....................", ln=1)

    # PAGINA 3: DECLARATIE
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 6, clean_text(f"{f_data['Nume']}"), ln=1)
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, clean_text(f"Adresa: {f_data['Adresa']}"), ln=1); pdf.cell(0, 5, f"RC: {f_data['RegCom']} | CUI: {f_data['CIF']}", ln=1)
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "DECLARATIE DE CONFORMITATE", align='C', ln=1); pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, clean_text(f"Noi, {f_data['Nume']}, cu sediul in {f_data['Adresa']}, declaram pe propria raspundere ca produsele livrate cu Avizul Nr. {order_no}/{data_azi} sunt conforme.")); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    for item in payload_fiscal: pdf.cell(0, 6, clean_text(f"- {item['Nomenclator Oficial']}"), ln=1)
    pdf.ln(20); pdf.cell(0, 6, "Manager,", ln=1); pdf.cell(0, 6, "Dan Donciu", ln=1)

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
    # Inițializări necesare modulului
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
                st.success(f"🔄 Sistemul a recunoscut aliasul: **{selected_option}** = **{prod_name}**")
            else:
                prod_name = selected_option
                alias_folosit = None

            p_data = st.session_state.db[prod_name]
            av_pal, av_box = get_available_stock_ui(prod_name)
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("📦 Stoc PALEȚI", av_pal)
            col_s2.metric("📦 Stoc CUTII (Libere)", av_box)
            col_s3.metric("🔄 Conversie WMS", f"{p_data['conversion']} cutii/palet")
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
                    force_reset()
                    st.rerun()

            st.divider()

            # AICI REVINE TABELUL SUPERB PENTRU COSUL DE CUMPARATURI
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
                    if st.button("👁️ Analizează Scindarea Dimo-NEXUS", type="primary", use_container_width=True):
                        st.session_state.client_temporar_comandat = client_ales
                        st.session_state.mod_previzualizare = True
                        st.rerun()

        # --- ECRAN B: PREVIZUALIZARE & SCINDARE ---
        else:
            client_ales_prev = st.session_state.client_temporar_comandat
            st.markdown("### 🔍 Previzualizare: Motor Dimo-NEXUS Activat")
            
            payload_logistic_curent = []
            payload_fiscal_curent = []
            
            for item in st.session_state.schita_comanda:
                nume_oficial = item['Produs']
                P = st.session_state.db[nume_oficial]['conversion']
                L = st.session_state.db[nume_oficial]['stock_box']
                C = item['Cutii']
                pallets_ordered = item['Paleti']
                
                if C > 0:
                    if (P - C) < C and L < C:
                        if pallets_ordered > 0:
                            payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})
                        payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Optimizare: EXTRAGE {P - C} cutii)", "Cant": "1", "UM": "PAL"})
                    else:
                        if pallets_ordered > 0:
                            payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})
                        if C <= L:
                            payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Culese din stoc liber)", "Cant": str(C), "UM": "Cutii"})
                        else:
                            if L > 0:
                                payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Goleste stoc liber)", "Cant": str(L), "UM": "Cutii"})
                            payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Box'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Din palet nou desfacut)", "Cant": str(C - L), "UM": "Cutii"})
                else:
                    if pallets_ordered > 0:
                        payload_logistic_curent.append({"Cod Gestiune": item['Cod_Depozit_Pal'], "Cod SB (NIR)": item['Cod_NIR'], "Denumire": f"{nume_oficial} (Sigilat)", "Cant": str(pallets_ordered), "UM": "PAL"})

                total_cutii = (pallets_ordered * P) + C
                total_unitati_baza = total_cutii * item['Conversie_Baza']
                
                payload_fiscal_curent.append({
                    "Cod_Depozit": item['Cod_Depozit_Pal'], "Cod SB (NIR)": item['Cod_NIR'],
                    "Nomenclator Oficial": nume_oficial, "Cantitate (U.M.)": f"{total_unitati_baza} {item['UM_Baza']}"
                })

            col_prism1, col_prism2 = st.columns(2)
            with col_prism1:
                st.warning("#### 🚚 Spre Stivuitorist (Logistic)")
                st.dataframe(pd.DataFrame(payload_logistic_curent)[['Cod Gestiune', 'Denumire', 'Cant', 'UM']], hide_index=True)

            with col_prism2:
                st.success("#### 🧾 Spre SmartBill (Fiscal)")
                st.dataframe(pd.DataFrame(payload_fiscal_curent)[['Cod SB (NIR)', 'Nomenclator Oficial', 'Cantitate (U.M.)']], hide_index=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔙 Întoarce-te (Editează coșul)"):
                    st.session_state.mod_previzualizare = False
                    st.rerun()
            with col_b2:
                if st.button("🚀 CONFIRMĂ ȘI LANSEAZĂ LA RAMPĂ", type="primary", use_container_width=True):
                    for item in st.session_state.schita_comanda:
                        prod = item['Produs']; P = st.session_state.db[prod]['conversion']; C = item['Cutii']; pallets_ordered = item['Paleti']
                        stoc_curent = get_total_boxes(prod)
                        stoc_ramas = stoc_curent - ((pallets_ordered * P) + C)
                        st.session_state.db[prod]['stock_pal'] = stoc_ramas // P
                        st.session_state.db[prod]['stock_box'] = stoc_ramas % P

                    st.session_state.istoric_comenzi_live.append({
                        "Comanda": st.session_state.order_number, "Client": client_ales_prev,
                        "Payload_Logistic": payload_logistic_curent, "Payload_Fiscal": payload_fiscal_curent,
                        "Status": "Asteapta Incarcare"
                    })
                    st.session_state.order_number += 1
                    st.session_state.schita_comanda = []
                    st.session_state.mod_previzualizare = False
                    st.rerun()

    with tab2:
        st.markdown("### 🚚 Confirmare & Emitere Acte WMS-Fiscal")
        if len(st.session_state.istoric_comenzi_live) == 0:
            st.info("Nicio mașină nu așteaptă la rampă.")
            
        for idx, cmd in enumerate(st.session_state.istoric_comenzi_live):
            st.markdown(f"#### Cmd NEXUS-{cmd['Comanda']} | {cmd['Client']}")
            st.write(f"Status curent: **{cmd['Status']}**")
            
            if cmd['Status'] == "Asteapta Incarcare":
                if st.button("✅ Confirmare: Marfa adusă la rampă", key=f"inc_{idx}"):
                    st.session_state.istoric_comenzi_live[idx]['Status'] = "Incarcat"
                    st.rerun()
                    
            elif cmd['Status'] == "Incarcat":
                if st.button("🖨️ EMITE SET ACTE (PDF 3 Pagini)", type="primary", key=f"emit_{idx}"):
                    pdf_p = generate_pdf_document(cmd['Comanda'], cmd['Client'], cmd['Payload_Fiscal'], cmd['Payload_Logistic'])
                    st.session_state.istoric_comenzi_live[idx]['Status'] = "Documente Generate"
                    st.session_state.istoric_comenzi_live[idx]['pdf_path'] = pdf_p
                    st.rerun()
                    
            elif cmd['Status'] == "Documente Generate":
                display_pdf(cmd['pdf_path'])
                with open(cmd['pdf_path'], "rb") as file:
                    st.download_button("📥 Descarcă Setul Complet", data=file, file_name=f"Acte_NEXUS_{cmd['Comanda']}.pdf", mime="application/pdf")
            st.divider()
