import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault")
    st.markdown("---")
    st.info("🔐 **Modul Vault**")
    st.info("🔐 **dB Back-up - zilnic / dB Back-up - săptămînal / dB Back-up Out of Office - săptămînal.**")


    
    st.success("""
    **Legislație:**
    
- Conform legislației contabile, termenul de păstrare pentru documente justificative și registre este de 5 ani.

- Situații financiare anuale: Se păstrează timp de 10 ani. Statele de plată și dosarele de personal: Se păstrează timp de 50 de ani.

- Legea permite păstrarea în format digital.
    """)
if st.button("⬅️ Înapoi la Panoul Principal"):
    st.session_state.current_module = 'Home'
    st.rerun()
