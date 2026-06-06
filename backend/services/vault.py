import streamlit as st

def render_vault_module():
    st.title("🛡️ Vault")
    st.markdown("---")
    st.info("🔐 Modul Vault - dB Back-up - zilnic / dB Back-up - săptămînal / dB Back-up Out of Office - săptămînal.")
    


    
    st.success("""
    **Exemplu de prompt:**
    
    La imaginea atașată te rog să faci următoarele modificări: 
    - Să ștergi logo-ul de sus: wipe it clean / Xxwoven 
    - Pentru a echilibra imaginea mută mai sus textul: XTRA PRECISION XP50 și rîndul de sub el
    - Înlocuiește la ”Packing: 50 sheets” 50 cu 90. Vom avea: ”Packing: 90 sheets”
    - Înlocuiește culoarea roșie la dunga roșie oblică din stînga-sus cu negru. (Deci negru în loc de roșu)
    - Înlocuiește culoarea roșie la triunghiul din stînga-jos cu culoare negru. (Deci negru în loc de roșu)
    - Înlocuiește codul de bare din imagine cu codul de bare din a doua imagine atașată.   
    
    *Img1_eticheta.pdf*  
    *Img2_Cod_de_bare.pdf*
    """)
if st.button("⬅️ Înapoi la Panoul Principal"):
    st.session_state.current_module = 'Home'
    st.rerun()
