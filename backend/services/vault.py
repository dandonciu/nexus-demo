import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault")
    st.markdown("---")
    st.info("🔐 Modul Vault")
     st.info("dB Back-up zilnic / dB Back-up săptmînal / dB Out of Office săptămînal).")
    if st.button("⬅️ Înapoi la Panoul Principal"):
        st.session_state.current_module = 'Home'
        st.rerun()
