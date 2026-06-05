

import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault")
    st.markdown("---")
     st.info("Back-up permanent, securizat, satisface Big4.")
    
    if st.button("⬅️ Înapoi la Panoul Principal"):
        st.session_state.current_module = 'Home'
           st.success("""
  dB Back-up zilnic
  dB Back-up săptămînal
  dB Out of Office săptămînal
    """)
        st.rerun()
