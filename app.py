import streamlit as st
from backend.services.order_orchestrator import render_lansare_module
from backend.database.clients_config import init_db
from backend.manager_analytics.kpi_dashboard import render_manager_dashboard

# Setări Pagină Enterprise (Rămâne mereu prima linie)
st.set_page_config(page_title="NEXUS B2B Enterprise", page_icon="🌌", layout="wide")

# ==========================================
# INIȚIALIZARE STĂRI GLOBALE
# ==========================================
if 'db' not in st.session_state: st.session_state.db = init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None
if 'current_module' not in st.session_state: st.session_state.current_module = 'Home'

def go_home(): st.session_state.current_module = 'Home'

# ==========================================
# ECRAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("""
        <div style="background: linear-gradient(90deg, #003366 0%, #004080 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 25px; text-align: center;">
            <h1 style="margin: 0;">🌌 NEXUS ENTERPRISE</h1>
            <p style="margin: 0; color: #a8c5e8;">Poartă Unică de Autentificare</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            pwd = st.text_input("Parolă Acces (angajat / manager)", type="password")
            if st.form_submit_button("Autentificare", use_container_width=True):
                if pwd in ["angajat", "manager"]:
                    st.session_state.logged_in = True
                    st.session_state.role = pwd
                    st.rerun()
                else: st.error("Acces Respins!")
    st.stop()

# ==========================================
# CSS PENTRU PLĂCI (TILES)
# ==========================================
st.markdown("""
    <style>
    .tile { background-color: #1E1E2E; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #3b3b54; transition: transform 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: white; }
    .tile:hover { transform: translateY(-5px); border-color: #00ADB5; }
    .tile h3 { color: #00ADB5; margin-bottom: 5px; }
    .tile p { font-size: 14px; color: #A6ACCD; }
    div[data-testid="stButton"] button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER MENIU RAPID
# ==========================================
c_logo, c_user, c_out = st.columns([8, 2, 1])
with c_logo: st.markdown("### 🌌 NEXUS Core Orchestrator")
with c_user: st.markdown(f"<div style='text-align:right; padding-top:10px; color:grey;'>Logat ca: <b>{st.session_state.role.upper()}</b></div>", unsafe_allow_html=True)
with c_out:
    if st.button("🚪 Logout"): 
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# ==========================================
# ORCHESTRATORUL: LANDING PAGE (CELE 6 PLĂCI)
# ==========================================
if st.session_state.current_module == 'Home':
    
    # RÂNDUL 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="tile"><h3>📦 Lansare Comenzi</h3><p>Convertor WMS-Fiscal & PDF</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Lansare", use_container_width=True, type="primary"):
            st.session_state.current_module = 'Lansare'
            st.rerun()

    with col2:
        st.markdown('<div class="tile"><h3>📊 Manager Analytics</h3><p>KPIs și Rapoarte Ședințe</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Dashboard", use_container_width=True):
            if st.session_state.role == "manager":
                st.session_state.current_module = 'Manager'
                st.rerun()
            else: st.toast("Acces restricționat. Doar Manager.", icon="⛔")

    with col3:
        st.markdown('<div class="tile"><h3>📨 Căsuța Turtă Dulce</h3><p>Preluare comenzi Email/Excel</p></div>', unsafe_allow_html=True)
        if st.button("Verifică Inbox", use_container_width=True):
            st.session_state.current_module = 'Email'
            st.rerun()

    # RÂNDUL 2
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown('<div class="tile"><h3>🎨 Etichete AI Secret</h3><p>Generare grafică protejată</p></div>', unsafe_allow_html=True)
        st.button("În Construcție 🚧", use_container_width=True, disabled=True, key="ai")

    with col5:
        st.markdown('<div class="tile"><h3>🧾 SmartBill Bot</h3><p>Injecție automată facturi</p></div>', unsafe_allow_html=True)
        st.button("În Construcție 🚧", use_container_width=True, disabled=True, key="sb")

    with col6:
        st.markdown('<div class="tile"><h3>🛡️ Vault & Arhivă</h3><p>Setări clienți și Backup</p></div>', unsafe_allow_html=True)
        st.button("În Construcție 🚧", use_container_width=True, disabled=True, key="vault")

# ==========================================
# RUTAREA CĂTRE MODULE
# ==========================================
elif st.session_state.current_module == 'Lansare':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    render_lansare_module()

elif st.session_state.current_module == 'Manager':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    render_manager_dashboard()
    
elif st.session_state.current_module == 'Email':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("📨 Căsuța de Turtă Dulce")
    st.info("Aici robotul NEXUS citește inbox-ul cautând PDF-uri sau Excel-uri de la clienți.")
