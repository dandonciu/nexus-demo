import streamlit as st
# DEBLOCARE TEMPORARĂ - ȘTERGE DUPĂ CE TESTEZI
from backend.auth.pin_auth import unblock_user
unblock_user("manager")
unblock_user("angajat")
unblock_user("admin")
st.success("DEBUG: Conturile au fost deblocate!")
from backend.database.clients_config import init_db
from backend.manager_analytics.kpi_dashboard import render_manager_dashboard
from backend.incoming_orders.email_parser import render_email_parser_module
from backend.services.order_orchestrator import render_lansare_module
from backend.services.etichete import render_etichete_module

st.set_page_config(page_title="NEXUS B2B Enterprise", page_icon="", layout="wide")

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
    
    # Dacă suntem în așteptarea 2FA, afișează formularul PIN
    if st.session_state.awaiting_2fa:
        from backend.auth.pin_auth import verify_2fa
        
        if verify_2fa(st.session_state.pending_2fa_user):
            # 2FA trecut cu succes
            st.session_state.logged_in = True
            st.session_state.role = st.session_state.pending_2fa_role
            st.session_state.awaiting_2fa = False
            st.session_state.pending_2fa_user = None
            st.rerun()
        else:
            # verify_2fa() deja afișează eroarea și formularul
            st.stop()
    
    # Altfel, afișează formularul de parolă
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            pwd = st.text_input("Parolă Acces (angajat / manager)", type="password")
            if st.form_submit_button("Autentificare", use_container_width=True):
               
            if pwd in ["angajat", "manager", "admin"]:
    # DEBUG - resetează PIN-urile (șterge această linie după ce funcționează)

            if pwd == "admin":
        from backend.auth.pin_auth import force_update_pins
        force_update_pins()
        st.info("PIN-uri resetate la noile valori!")
    
    st.session_state.awaiting_2fa = True
    st.session_state.pending_2fa_user = pwd
    st.session_state.pending_2fa_role = pwd
    st.rerun()    
                else:
                    st.error("Acces Respins!")
    st.stop()

# ========== RESTUL APLICAȚIEI (doar dacă e logat) ==========
# Aici vine dashboard-ul tău, modulele, etc.

st.markdown("""
<style>
.tile { background-color: #1E1E2E; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #3b3b54; transition: transform 0.2s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: white; height: 130px; display: flex; flex-direction: column; justify-content: center;}
.tile:hover { transform: translateY(-5px); border-color: #00ADB5; }
.tile h3 { color: #00ADB5; margin-bottom: 5px; font-size: 1.2rem; }
.tile p { font-size: 13px; color: #A6ACCD; margin: 0; }
div[data-testid="stButton"] button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

c_logo, c_user, c_out = st.columns([8, 2, 1])
with c_logo: st.markdown("### 🌌 NEXUS Core Orchestrator")
with c_user: st.markdown(f"<div style='text-align:right; padding-top:10px; color:grey;'>Logat ca: <b>{st.session_state.role.upper()}</b></div>", unsafe_allow_html=True)
with c_out:
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()
st.divider()

if st.session_state.current_module == 'Home':
    st.markdown("#### ⚡ Flux Operațional")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="tile"><h3>📦 Lansare Comenzi</h3><p>Ieșiri, WMS, Avize PDF</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Lansare", use_container_width=True, type="primary"): st.session_state.current_module = 'Lansare'; st.rerun()

    with col2:
        st.markdown('<div class="tile"><h3>📥 Recepție & NIR</h3><p>Intrări marfă în Gestiune</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Recepție", use_container_width=True): st.session_state.current_module = 'Receptie'; st.rerun()

    with col3:
        st.markdown('<div class="tile"><h3>🚚 Modul Transport</h3><p>Comenzi Curier & Status</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Transport", use_container_width=True): st.session_state.current_module = 'Transport'; st.rerun()

    with col4:
        st.markdown('<div class="tile"><h3>🧾 SmartBill HUB</h3><p>Facturare & Contabilitate</p></div>', unsafe_allow_html=True)
        if st.button("Deschide SmartBill", use_container_width=True): st.session_state.current_module = 'SmartBill'; st.rerun()

    st.markdown("<br>#### 🛠️ Instrumente, AI & Analiză", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown('<div class="tile"><h3>📨 Inbox Auto-Procesare</h3><p>Email B2B & Auto-Reply</p></div>', unsafe_allow_html=True)
        if st.button("Verifică Inbox", use_container_width=True): st.session_state.current_module = 'Email'; st.rerun()

    with col6:
        st.markdown('<div class="tile"><h3> Studio Etichete AI</h3><p>Editare PDF/JPG cu AI</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Studio", use_container_width=True): st.session_state.current_module = 'Etichete'; st.rerun()

    with col7:
        st.markdown('<div class="tile"><h3>📊 Manager Analytics</h3><p>KPIs & Istoric Livrări</p></div>', unsafe_allow_html=True)
        if st.button("Deschide Dashboard", use_container_width=True):
            if st.session_state.role == "manager": st.session_state.current_module = 'Manager'; st.rerun()
            else: st.error("⛔ Interzis. Doar Manager.")

    with col8:
        st.markdown('<div class="tile"><h3>🛡️ Vault Clienți</h3><p>Setări, Baze Date, Backup</p></div>', unsafe_allow_html=True)
        st.button("În Construcție 🚧", use_container_width=True, disabled=True, key="vault")

elif st.session_state.current_module == 'Lansare':
    st.button("️ Înapoi la Panoul Principal", on_click=go_home)
    render_lansare_module()
elif st.session_state.current_module == 'Manager':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    render_manager_dashboard()
elif st.session_state.current_module == 'Email':
    st.button("️ Înapoi la Panoul Principal", on_click=go_home)
    render_email_parser_module()
elif st.session_state.current_module == 'Receptie':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("📥 Modul Recepție Marfă")
    st.info("📥 Modul Recepție Marfă -> În Dezvoltare")
elif st.session_state.current_module == 'Transport':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("🚚 Modul Transport & Curieri")
    st.info("🚚 Modul Transport -> În Dezvoltare")
elif st.session_state.current_module == 'SmartBill':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("🧾 SmartBill HUB")
    c1, c2 = st.columns(2)
    c1.button("Ramura A: Facturare & Gestiune", use_container_width=True)
    c2.button("Ramura B: Contabilitate & Încasări", use_container_width=True)
elif st.session_state.current_module == 'Etichete':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    render_etichete_module()
