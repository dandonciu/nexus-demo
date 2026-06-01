import streamlit as st

st.set_page_config(page_title="Studio Etichete AI", page_icon="🏷️", layout="wide")

st.title("🏷️ Studio Etichete AI (Grand Prix)")
st.markdown("Procesare grafică automatizată pentru etichete via OpenAI.")
st.divider()

# Caseta cu exemplul de prompt cerută de tine:
st.info("""
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

# Aici va urma restul codului pentru upload fisiere si API OpenAI...
st.file_uploader("Încarcă fișierele (PDF/JPG)", accept_multiple_files=True)
st.text_area("Introdu prompt-ul tău aici:")
st.button("Procesează Eticheta 🚀")
