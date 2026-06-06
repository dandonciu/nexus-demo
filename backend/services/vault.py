import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault")
    st.markdown("---")
    st.info("🔐 Modul Vault")
    st.info("dB Back-up - zilnic / dB Back-up - săptămînal / dB Back-up Out of Office - săptămînal).")
    st.info("- Conform legislației contabile actuale, termenul de păstrare pentru anumite documente justificative și registre este de 5 ani.")
    st.info("- Legea permite păstrarea în format digital.")


if st.button("⬅️ Înapoi la Panoul Principal"):
    st.session_state.current_module = 'Home'
    st.rerun()
