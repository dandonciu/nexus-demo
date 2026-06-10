import streamlit as st

from backend.database.clients_config import init_db
from backend.manager_analytics.kpi_dashboard import render_manager_dashboard
from backend.incoming_orders.email_parser import render_email_parser_module
from backend.services.order_orchestrator import render_lansare_module
from backend.services.etichete import render_etichete_module
from backend.services.vault import render_vault_module   # ← linia asta

st.set_page_config(page_title="NEXUS B2B Enterprise", page_icon="🌌", layout="wide")

if 'db' not in st.session_state: st.session_state.db = init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None
if 'current_module' not in st.session_state: st.session_state.current_module = 'Home'
if 'awaiting_2fa' not in st.session_state: st.session_state.awaiting_2fa = False
if 'pending_2fa_user' not in st.session_state: st.session_state.pending_2fa_user = None

def go_home(): st.session_state.current_module = 'Home'

# ========== LOGIN + 2FA ==========
if not st.session_state.logged_in:
    st.markdown("""
        <div style="background: linear-gradient(90deg, #003366 0%, #004080 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 25px; text-align: center;">
            <h1 style="margin: 0;">🌌 NEXUS ENTERPRISE</h1>
            <p style="margin: 0; color: #a8c5e8;">Poartă Unică de Autentificare</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("awaiting_2fa", False):
        from backend.auth.pin_auth import verify_2fa
        if verify_2fa(st.session_state.pending_2fa_user):
            st.session_state.logged_in = True
            st.session_state.role = st.session_state.pending_2fa_role
            st.session_state.awaiting_2fa = False
            st.session_state.pending_2fa_user = None
            st.rerun()
        else:
            st.stop()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            pwd = st.text_input("Parolă Acces", type="password")
            submitted = st.form_submit_button("Autentificare", use_container_width=True)
            
            if submitted:
                # Verificare strictă
                if pwd == "angajat":
                    role = "angajat"
                    st.session_state.awaiting_2fa = True
                    st.session_state.pending_2fa_user = role
                    st.session_state.pending_2fa_role = role
                    st.rerun()
                elif pwd == "manager":
                    role = "manager"
                    st.session_state.awaiting_2fa = True
                    st.session_state.pending_2fa_user = role
                    st.session_state.pending_2fa_role = role
                    st.rerun()
                elif pwd == "admin":
                    role = "admin"
                    st.session_state.awaiting_2fa = True
                    st.session_state.pending_2fa_user = role
                    st.session_state.pending_2fa_role = role
                    st.rerun()
                else:
                    st.error("❌ Parolă greșită! Încearcă: angajat, manager sau admin")
    
    st.stop()

# ========== DASHBOARD ==========
st.markdown("""
<style>
.tile { background-color: #1E1E2E; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #3b3b54; transition: transform 0.2s ease; margin-bottom: 15px; color: white; height: 130px; display: flex; flex-direction: column; justify-content: center;}
.tile:hover { transform: translateY(-5px); border-color: #00ADB5; }
.tile h3 { color: #00ADB5; margin-bottom: 5px; font-size: 1.2rem; }
.tile p { font-size: 13px; color: #A6ACCD; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CSS GLOBAL PENTRU ELIMINAREA SPAȚIILOR GOALE (Fără a tăia vizualul)
# ==========================================
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER MENIU RAPID (PE UN SINGUR RÂND COMPACT)
# ==========================================
c_logo, c_empty, c_user, c_out = st.columns([5, 3, 2, 1])

with c_logo: 
    # Banner discret, fără background, cu chenar fin
    st.markdown("""
        <div style="padding: 5px 15px; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 6px; display: inline-block; margin-top: 5px;">
            <h1 style="margin: 0; font-weight: 800; font-size: 1.5rem;">🌌 NEXUS ORCHESTRATOR</h1>
            <p style="margin: 0; color: gray; font-size: 0.85rem;">Sistem Unic de Gestiune, Reconciliere și Automatizare</p>
        </div>
    """, unsafe_allow_html=True)

with c_user: 
    # Aliniere perfectă cu butonul
    st.markdown(f"<div style='text-align:right; margin-top: 20px; color:grey; font-size:0.9rem;'>Logat ca: <b>{st.session_state.role.upper()}</b></div>", unsafe_allow_html=True)

with c_out:
    # Împingem butonul puțin mai jos ca să fie în linie cu textul
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True): 
        st.session_state.logged_in = False; st.rerun()

if st.session_state.current_module == 'Home':
    st.markdown("#### ⚡ Flux Operațional")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="tile"><h3>📦 Lansare Comenzi</h3><p>Ieșiri, WMS, Avize PDF</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Lansare", use_container_width=True): st.session_state.current_module = 'Lansare'; st.rerun()
    with col2:
        st.markdown('<div class="tile"><h3>📥 Recepție & NIR</h3><p>Intrări marfă</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Recepție", use_container_width=True): st.session_state.current_module = 'Receptie'; st.rerun()
    with col3:
        st.markdown('<div class="tile"><h3>🚚 TraceHub</h3><p>(Log Nexus)</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Log Nexus", use_container_width=True): st.session_state.current_module = 'Transport'; st.rerun()
    with col4:
        st.markdown('<div class="tile"><h3>🧾 SmartBill HUB</h3><p>Facturare</p></div>', unsafe_allow_html=True)
        if st.button("Deschide SmartBill", use_container_width=True): st.session_state.current_module = 'SmartBill'; st.rerun()
    
    st.markdown("<br>#### 🛠️ Instrumente", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown('<div class="tile"><h3>📨 Inbox Auto</h3><p>Email B2B</p></div>', unsafe_allow_html=True)
        if st.button("Verifică Inbox", use_container_width=True): st.session_state.current_module = 'Email'; st.rerun()
    with col6:
        st.markdown('<div class="tile"><h3>🎨 Etichete AI</h3><p>Editare PDF</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Studio", use_container_width=True): st.session_state.current_module = 'Etichete'; st.rerun()
    with col7:
        st.markdown('<div class="tile"><h3>📊 Manager Analytics</h3><p>KPIs</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Dashboard", use_container_width=True):
            if st.session_state.role == "manager": st.session_state.current_module = 'Manager'; st.rerun()
            else: st.error("⛔ Doar Manager")
    with col8:
        st.markdown('<div class="tile"><h3>🛡️ Vault</h3><p>Setări, Baze Date, Backup</p></div>', unsafe_allow_html=True)
        if st.button("Acces", use_container_width=True):
            if st.session_state.role == "manager": 
                st.session_state.current_module = 'vault'
                st.rerun()
            else: 
                st.error("⛔ Doar Manager")
        
elif st.session_state.current_module == 'Lansare':
    st.button("⬅️ Înapoi", on_click=go_home)
    render_lansare_module()
elif st.session_state.current_module == 'Manager':
    st.button("⬅️ Înapoi", on_click=go_home)
    render_manager_dashboard()
elif st.session_state.current_module == 'Email':
    st.button("⬅️ Înapoi", on_click=go_home)
    render_email_parser_module()
elif st.session_state.current_module == 'Etichete':
    st.button("⬅️ Înapoi", on_click=go_home)
    render_etichete_module() 
elif st.session_state.current_module == 'vault':
    st.button("⬅️ Înapoi", on_click=go_home)
    render_vault_module()

