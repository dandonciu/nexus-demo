import streamlit as st

# Setări Pagină Enterprise
st.set_page_config(page_title="NEXUS B2B Enterprise", page_icon="🌌", layout="wide")

# Inițializare stare pentru navigare
if 'current_module' not in st.session_state:
    st.session_state['current_module'] = 'Home'

def go_home():
    st.session_state['current_module'] = 'Home'

# --- STILIZARE CSS PENTRU PLĂCI (TILES) ---
st.markdown("""
    <style>
    .tile {
        background-color: #1E1E2E;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #3b3b54;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        color: white;
    }
    .tile:hover {
        transform: translateY(-5px);
        border-color: #00ADB5;
    }
    .tile h3 { color: #00ADB5; margin-bottom: 5px; }
    .tile p { font-size: 14px; color: #A6ACCD; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ECRANUL PRINCIPAL (LANDING PAGE)
# ==========================================
if st.session_state['current_module'] == 'Home':
    st.title("🌌 NEXUS B2B : Panou de Comandă")
    st.markdown("Selectează un modul pentru a începe fluxul de lucru.")
    st.divider()

    # RÂNDUL 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="tile"><h3>📦 Lansare Comenzi</h3><p>Convertor Gestiune-Fiscal & PDF</p></div>', unsafe_allow_html=True)
        if st.button("Accesează Lansare", use_container_width=True, key="btn_lansare"):
            st.session_state['current_module'] = 'Lansare'
            st.rerun()

    with col2:
        st.markdown('<div class="tile"><h3>🎨 Etichete AI Secret</h3><p>Generare etichete logistice</p></div>', unsafe_allow_html=True)
        if st.button("Accesează Studio", use_container_width=True, key="btn_ai"):
            st.session_state['current_module'] = 'Etichete'
            st.rerun()

    with col3:
        st.markdown('<div class="tile"><h3>🧾 SmartBill Bot</h3><p>Injecție automată facturi</p></div>', unsafe_allow_html=True)
        if st.button("Accesează Bot", use_container_width=True, key="btn_smartbill"):
            st.session_state['current_module'] = 'SmartBill'
            st.rerun()

    # RÂNDUL 2
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<div class="tile"><h3>📨 Căsuța Turtă Dulce</h3><p>Preluare comenzi Email/Excel</p></div>', unsafe_allow_html=True)
        if st.button("Verifică Inbox", use_container_width=True, key="btn_email"):
            st.session_state['current_module'] = 'Email'
            st.rerun()

    with col5:
        st.markdown('<div class="tile"><h3>📊 Manager Analytics</h3><p>KPIs și Rapoarte Ședințe</p></div>', unsafe_allow_html=True)
        if st.button("Vezi Rapoarte", use_container_width=True, key="btn_manager"):
            st.session_state['current_module'] = 'Manager'
            st.rerun()

    with col6:
        st.markdown('<div class="tile"><h3>🛡️ Vault & Arhivă</h3><p>Setări clienți și Backup HDD</p></div>', unsafe_allow_html=True)
        if st.button("Intră în Vault", use_container_width=True, key="btn_vault"):
            st.session_state['current_module'] = 'Vault'
            st.rerun()

# ==========================================
# RUTAREA CĂTRE MODULE (MOCKUP PENTRU ACUM)
# ==========================================
elif st.session_state['current_module'] == 'Lansare':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("📦 Modul: Lansare Comenzi")
    st.info("Aici vom importa logica ta de 330 de linii (decuplată din backend). Aștept codul!")
    # Aici va veni: from backend.services.order_orchestrator import render_order_ui ...

elif st.session_state['current_module'] == 'Email':
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title("📨 Căsuța de Turtă Dulce (Email Parser)")
    st.warning("Botul citește inbox-ul cautând PDF-uri sau fișiere Excel de la clienți...")
    
# [Aici putem adăuga elif-uri pentru restul modulelor în viitor]
else:
    st.button("⬅️ Înapoi la Panoul Principal", on_click=go_home)
    st.title(f"Modul în construcție: {st.session_state['current_module']}")
