import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault Clienți")
    st.markdown("---")
    st.info("🔐 Modul Vault")
    
    if st.button("⬅️ Înapoi la Panoul Principal"):
        st.session_state.current_module = 'Home'
        st.rerun()
           st.success("""
  dB Back-up zilnic
  dB Back-up săptămînal
  dB Out of Office săptămînal
    """)
        st.rerun()
