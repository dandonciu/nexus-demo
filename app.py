import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database.clients_config import init_db

# LINIA DE SALVARE: Setează layout-ul pe ecran lat și titlul filei din browser
st.set_page_config(layout="wide", page_title="NexusDS", page_icon="🌌")

# Import module operaționale originale
from backend.services.order_orchestrator import render_lansare_module
from backend.services.workflow import render_workflow_module, get_active_tasks_count

# =========================================================================
# 🌌 CONECTORI DE IMPORT SECURIZAȚI PENTRU MODULELE TALE PREEXISTENTE
# =========================================================================

# 1. Inbox Central (inbox_central.py)
try:
    from backend.incoming_orders.inbox_central import render_inbox_central_module
except ImportError:
    def render_inbox_central_module(): st.info("📂 Modulul 'Inbox Central' (inbox_central.py) este pregătit pentru conectare.")

# 2. Manager Analytics (views/dashboard_view.py)
try:
    from backend.manager_analytics.views.dashboard_view import render_manager_dashboard
except ImportError:
    try:
        from backend.manager_analytics.kpi_dashboard import render_manager_dashboard
    except ImportError:
        def render_manager_dashboard(): st.info("📂 Modulul 'Manager Analytics' este pregătit pentru conectare.")

# 3. Recepție & NIR (receptie_nir.py)
try:
    from backend.incoming_orders.receptie_nir import render_receptie_module
except ImportError:
    def render_receptie_module(): st.info("📂 Modulul 'Recepție & NIR' (receptie_nir.py) este pregătit pentru conectare.")

# 4. SmartBill HUB (smartbill.py)
try:
    from backend.services.smartbill import render_smartbill_module
except ImportError:
    def render_smartbill_module(): st.info("📂 Modulul 'SmartBill HUB' (smartbill.py) este pregătit pentru conectare.")

# 5. TraceHub (trace_hub.py)
try:
    from backend.services.trace_hub import render_trace_hub_module
except ImportError:
    def render_trace_hub_module(): st.info("📂 Modulul 'TraceHub' (trace_hub.py) este pregătit pentru conectare.")

# 6. Vault Securizat (vault.py)
try:
    from backend.services.vault import render_vault_module
except ImportError:
    def render_vault_module(): st.info("📂 Modulul 'Vault Securizat' (vault.py) este pregătit pentru conectare.")

# 7. Studio AI / Etichete (etichete.py)
try:
    from backend.services.etichete import render_etichete_module
except ImportError:
    def render_etichete_module(): st.info("📂 Modulul 'Studio AI' (etichete.py) este pregătit pentru conectare.")

# 8. Gestiune Stocuri (gestiune_stocuri.py)
try:
    from backend.services.gestiune_stocuri import render_gestiune_stocuri_module
except ImportError:
    def render_gestiune_stocuri_module(): st.info("📂 Modulul 'Gestiune Stocuri/Inventar' (gestiune_stocuri.py) este pregătit pentru conectare.")

# 9. Anticamera de Triaj (triaj.py)
try:
    from backend.incoming_orders.triaj import render_triaj_module
except ImportError:
    def render_triaj_module(): st.info("📂 Modulul 'Anticamera de Triaj' (triaj.py) este pregătit pentru conectare.")


# =========================================================================
# 🌌 INITIALIZARE SI SETARI PORTAL
# =========================================================================

if 'db' not in st.session_state: 
    st.session_state.db = init_db()
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'role' not in st.session_state: 
    st.session_state.role = None
if 'current_module' not in st.session_state: 
    st.session_state.current_module = 'Home'
if 'awaiting_2fa' not in st.session_state: 
    st.session_state.awaiting_2fa = False
if 'pending_2fa_user' not in st.session_state: 
    st.session_state.pending_2fa_user = None

if 'active_lansare_tab' not in st.session_state:
    st.session_state.active_lansare_tab = 0

if 'task_list' not in st.session_state:
    st.session_state.task_list = [
        {"Status": False, "Cine_Raspunde": "Claudia", "Adaugat_de": "Manager", "Sarcina": "Verificare stoc BKTp721", "Termen_Limita": "21.01.2025", "Completat_la_data": "-"}
    ]
if 'trace_logs' not in st.session_state:
    st.session_state.trace_logs = [
        {"Timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S'), "User": "System", "Actiune": "Sistem NexusDS pornit."}
    ]

def go_home(): 
    st.session_state.current_module = 'Home'

# LISTA STRICTĂ DE 10 MODULE
MODULES_CONFIG = [
    {"id": "Workflow", "title": "Registru de Sarcini", "avatar": "RS", "color": "#10b981", "desc": "Managementul sarcinilor logistice zilnice. Activități automate de stoc și alerte.", "category": "Logistică & Operațiuni"},
    {"id": "Inbox", "title": "Inbox Central", "avatar": "IC", "color": "#f59e0b", "desc": "Monitorizare e-mailuri primite. Descărcare atașamente PDF/Excel.", "category": "Logistică & Operațiuni"},
    {"id": "Lansare", "title": "Lansare Comenzi", "avatar": "LC", "color": "#0284c7", "desc": "Optimizare WMS. Include Anticamera de triere (Tab 1), workbench-ul original de calcul și rampa.", "category": "Logistică & Operațiuni"},
    {"id": "Analytics", "title": "Manager Analytics", "avatar": "AN", "color": "#6366f1", "desc": "Control Panel cu indicatori KPI, istoric consum clienți și estimări.", "category": "Audit & Financiar"},
    {"id": "Receptie", "title": "Recepție & NIR", "avatar": "RC", "color": "#14b8a6", "desc": "Înregistrarea facturilor de intrare asistată de AI cu generare NIR.", "category": "Logistică & Operațiuni"},
    {"id": "SmartBill", "title": "SmartBill HUB", "avatar": "SB", "color": "#8b5cf6", "desc": "Interconectare cu serviciile de facturare și nomenclatoare API.", "category": "Audit & Financiar"},
    {"id": "TraceHub", "title": "TraceHub", "avatar": "TH", "color": "#ec4899", "desc": "Trasabilitate completă. Înregistrează automat acțiunile utilizatorilor (audit).", "category": "Audit & Financiar"},
    {"id": "Vault", "title": "Vault Securizat", "avatar": "VT", "color": "#ef4444", "desc": "Arhivă securizată gata de audit Big4. Backup documente fiscale pe termen lung.", "category": "Audit & Financiar"},
    {"id": "Etichete", "title": "Studio AI", "avatar": "AI", "color": "#f43f5e", "desc": "Design etichete WMS iterativ cu asistent AI și export PDF.", "category": "Integrare AI"},
    {"id": "Stocuri", "title": "Gestiune Stocuri/Inventar", "avatar": "ST", "color": "#0f766e", "desc": "Vizualizare raft live, ajustări de reconciliere și modificări ambalare WMS.", "category": "Logistică & Operațiuni"}
]

# ========== SECȚIUNE LOGIN ==========
if not st.session_state.logged_in:
    st.markdown("""
        <div style="background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%); padding: 1rem; border-radius: 0.5rem; color: white; margin-bottom: 1rem; text-align: center;">
            <h2 style="margin: 0; font-size: 1.5rem; letter-spacing: 1px;">🌌 NexusDS ENTERPRISE</h2>
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
            pwd = st.text_input("Parolă de Acces", type="password")
            submitted = st.form_submit_button("Pasul următor (PIN)", use_container_width=True)
            if submitted:
                normalized_pwd = pwd.lower().strip()
                if normalized_pwd in ["angajat", "manager", "admin"]:
                    st.session_state.awaiting_2fa = True
                    st.session_state.pending_2fa_user = normalized_pwd
                    st.session_state.pending_2fa_role = normalized_pwd
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
    st.stop()


# ========== SIDEBAR MINIMALIST & DECORATIV ==========
with st.sidebar:
    st.markdown("### 🌌 NexusDS")
    st.info(f"👤 **Utilizator:** {st.session_state.role.upper()}")
    
    if st.session_state.current_module != 'Home':
        st.divider()
        if st.button("⬅️ Panoul Principal", use_container_width=True):
            go_home()
            st.rerun()
            
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.current_module = 'Home'
        st.rerun()


# ========== BARE NOTIFICĂRI ORIZONTALE ==========
def render_top_banners():
    critice = sum(1 for k, v in st.session_state.db.items() if ((v['stock_pal'] * v['conversion']) + v['stock_box']) < 150)
    unapproved_triaj = sum(1 for x in st.session_state.get('triaj_data', []) if not x.get('Aprobat', False))
    la_rampa = sum(1 for x in st.session_state.get('istoric_comenzi_live', []) if x['Status'] in ["Asteapta Incarcare", "Incarcat", "Draft Acte"])

    cols_alerts = st.columns(4)
    with cols_alerts[0]:
        if unapproved_triaj > 0:
            if st.button(f"📥 Triaj: {unapproved_triaj} solicitări - Verifică în Triaj!", type="secondary", use_container_width=True):
                st.session_state.current_module = 'Lansare'
                st.session_state.active_lansare_tab = 0
                st.rerun()
        else:
            st.button("🟢 Nimic urgent în Triaj", disabled=True, use_container_width=True)
            
    with cols_alerts[1]:
        if la_rampa > 0:
            if st.button(f"🚚 Rampă: {la_rampa} comenzi - Verifică în Rampă!", type="secondary", use_container_width=True):
                st.session_state.current_module = 'Lansare'
                st.session_state.active_lansare_tab = 2
                st.rerun()
        else:
            st.button("🟢 Rampă liberă", disabled=True, use_container_width=True)

    with cols_alerts[2]:
        if critice > 0:
            if st.button(f"⚠️ Atenție stoc scăzut - Verifică Gestiune!", type="secondary", use_container_width=True):
                st.session_state.current_module = 'Stocuri'
                st.rerun()
        else:
            st.button("🟢 Stocuri în parametri", disabled=True, use_container_width=True)

    with cols_alerts[3]:
        st.button("🟢 Livrări Furnizor: OK", disabled=True, use_container_width=True)


# ========== STYLE COMPACT RESPONSIV (VALORI RELATIVE / REM) ==========
st.markdown('''
    <style>
    .m365-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0.35rem;
        padding: 0.65rem;
        min-height: 7.2rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        margin-bottom: 0.5rem;
        color: #1e293b;
    }
    .m365-card:hover {
        border-color: #0284c7;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .card-header-box {
        display: flex;
        align-items: center;
        margin-bottom: 0.25rem;
    }
    .card-avatar {
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 0.25rem;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 0.5rem;
        font-size: 0.75rem;
    }
    .card-title-box {
        font-weight: 600;
        font-size: 0.85rem;
        color: #0f172a;
        margin: 0;
    }
    .card-body-text {
        font-size: 0.7rem;
        color: #475569;
        line-height: 1.3;
        margin-bottom: 0px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;  
        overflow: hidden;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
    div[data-testid="stForm"] {
        padding: 0.75rem !important;
    }
    </style>
''', unsafe_allow_html=True)


# ========== COCKPIT CENTRAL ==========
if st.session_state.current_module == 'Home':
    st.markdown("### 🌌 Catalog Servicii NexusDS")
    render_top_banners()
    
    st.write("")
    
    filter_tab = st.radio(
        "Filtru:", ["Toate", "Logistică & Operațiuni", "Audit & Financiar", "Integrare AI"],
        horizontal=True, label_visibility="collapsed"
    )
    
    # Afișare Toast cu auto-dispoziție dacă există avertisment de securitate
    if st.session_state.get('auth_warning'):
        st.toast(st.session_state.auth_warning, icon="🔒")
        st.session_state.auth_warning = None
        
    st.divider()

    filtered_modules = [m for m in MODULES_CONFIG if filter_tab == "Toate" or m["category"] == filter_tab]

    cols_per_row = 4
    for i in range(0, len(filtered_modules), cols_per_row):
        row_modules = filtered_modules[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, module in enumerate(row_modules):
            with cols[idx]:
                st.markdown(f"""
                    <div class="m365-card">
                        <div>
                            <div class="card-header-box">
                                <div class="card-avatar" style="background-color: {module['color']};">{module['avatar']}</div>
                                <div class="card-title-box">{module['title']}</div>
                            </div>
                            <div class="card-body-text">{module['desc']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # INLINE SECURITY FILTER (FĂRĂ REDIRECT)
                if st.button("Lansează", key=f"btn_{module['id']}", use_container_width=True):
                    if st.session_state.role == "angajat" and module['id'] in ["Analytics", "Vault", "TraceHub"]:
                        st.session_state.auth_warning = f"⛔ Acces Restricționat pentru {module['title']}!"
                        st.rerun()
                    else:
                        st.session_state.auth_warning = None
                        st.session_state.current_module = module['id']
                        st.rerun()

# ========== NAVIGARE MODULE CU CONECTORI DIRECTI ==========
else:
    if st.session_state.current_module == 'Lansare':
        render_lansare_module()
    elif st.session_state.current_module == 'Triaj':
        render_triaj_module()
    elif st.session_state.current_module == 'Inbox':
        render_inbox_central_module()
    elif st.session_state.current_module == 'Workflow':
        render_workflow_module()
    elif st.session_state.current_module == 'TraceHub':
        render_trace_hub_module()
    elif st.session_state.current_module == 'Analytics':
        render_manager_dashboard()
    elif st.session_state.current_module == 'Receptie':
        render_receptie_module()
    elif st.session_state.current_module == 'SmartBill':
        render_smartbill_module()
    elif st.session_state.current_module == 'Etichete':
        render_etichete_module()
    elif st.session_state.current_module == 'Vault':
        render_vault_module()
    elif st.session_state.current_module == 'Stocuri':
        render_gestiune_stocuri_module()
