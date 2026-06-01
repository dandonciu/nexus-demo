import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import base64
import tempfile
from fpdf import FPDF
from backend.database.clients_config import clients_data, furnizor_data, client_aliases

PDF_DIR = tempfile.gettempdir()

def force_reset(): 
    st.session_state.reset_counter += 1

def reset_cart():
    st.session_state.schita_comanda = []
    st.session_state.last_success_msg = None
    force_reset()

def clean_text(txt):
    replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
    for k, v in replacements.items(): 
        txt = str(txt).replace(k, v)
    return txt

def get_total_boxes(prod_key): 
    return (st.session_state.db[prod_key]['stock_pal'] * st.session_state.db[prod_key]['conversion']) + st.session_state.db[prod_key]['stock_box']

def get_available_stock_ui(prod_key):
    rem = get_total_boxes(prod_key) - sum([(i.get('Paleti', 0) * st.session_state.db[prod_key]['conversion']) + i.get('Cutii', 0) for i in st.session_state.schita_comanda if i.get('Produs') == prod_key])
    return rem // st.session_state.db[prod_key]['conversion'], rem % st.session_state.db[prod_key]['conversion']

def calculate_delta(prod_key, cmd_pal, cmd_box):
    return ((cmd_pal * st.session_state.db[prod_key]['conversion']) + cmd_box + sum([(i['Paleti'] * st.session_state.db[prod_key]['conversion']) + i['Cutii'] for i in st.session_state.schita_comanda if i['Produs'] == prod_key])) <= get_total_boxes(prod_key)

# --- MOTOR PDF ---
def generate_pdf_document(order_no, client_name, payload_fiscal, payload_log):
    pdf = FPDF()
    c_data = clients_data[client_name]
    f_data = furnizor_data
    data_azi = datetime.now().strftime('%d/%m/%Y')
    
    # PAGINA 1: AVIZ
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "AVIZ DE INSOTIRE A MARFII", align='C', ln=1)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Seria NS nr. {order_no} | Data: {data_azi}", align='C', ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 9)
    pdf.cell(95, 5, clean_text(f"Furnizor: {f_data['Nume']}"), ln=0)
    pdf.set_x(110)
    pdf.cell(85, 5, clean_text(f"Client: {client_name}"), ln=1)
    
    pdf.set_font("Arial", '', 8)
    pdf.cell(95, 4, f"CIF: {f_data['CIF']} | J: {f_data['RegCom']}", ln=0)
    pdf.set_x(110)
    pdf.cell(85, 4, f"CIF: {c_data['CIF']} | J: {c_data['RegCom']}", ln=1)
    pdf.cell(95, 4, clean_text(f"Adresa: {f_data['Adresa']}"), ln=0)
    pdf.set_x(110)
    pdf.multi_cell(85, 4, clean_text(f"Adresa: {c_data['Adresa']}"))
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 8)
    pdf.cell(10, 8, "Nr.", 1, 0
