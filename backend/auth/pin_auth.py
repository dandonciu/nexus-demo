"""
Modul 2FA simplu cu PIN fix + blocare după 3 încercări
Pentru MVP Nexus - poate fi înlocuit mai târziu cu Google Authenticator
"""

import streamlit as st
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

# ========== CONFIGURARE ==========
PIN_FILE = Path(__file__).parent / "pins.json"
LOGIN_ATTEMPTS_KEY = "pin_failed_attempts"  # cheie în session_state
BLOCK_DURATION_MINUTES = 30
MAX_ATTEMPTS = 3

# ========== ÎNCARCĂ PIN-URILE ==========
def load_pins():
    """Încarcă PIN-urile hash-uite din fișierul JSON"""
    if not PIN_FILE.exists():
        # Fișier demo dacă nu există
        default_pins = {
            "admin": hashlib.sha256("111111".encode()).hexdigest(),
            "manager": hashlib.sha256("222222".encode()).hexdigest(),
            "contabil": hashlib.sha256("333333".encode()).hexdigest(),
            "angajat": hashlib.sha256("444444".encode()).hexdigest()
        }
        with open(PIN_FILE, "w") as f:
            json.dump(default_pins, f, indent=2)
        return default_pins
    
    with open(PIN_FILE, "r") as f:
        return json.load(f)

# ========== SALVEAZĂ PIN-URILE ==========
def save_pins(pins_dict):
    """Salvează PIN-urile hash-uite în fișier"""
    with open(PIN_FILE, "w") as f:
        json.dump(pins_dict, f, indent=2)

# ========== VERIFICARE BLOCARE ==========
def is_blocked(username):
    """Verifică dacă utilizatorul este blocat temporar"""
    if f"blocked_until_{username}" not in st.session_state:
        return False
    
    block_until = st.session_state[f"blocked_until_{username}"]
    if datetime.now() < block_until:
        return True
    
    # Blocarea a expirat
    del st.session_state[f"blocked_until_{username}"]
    st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0
    return False

# ========== ÎNREGISTREAZĂ ÎNCERCARE EȘUATĂ ==========
def register_failed_attempt(username):
    """Înregistrează o încercare eșuată și blochează dacă se atinge limita"""
    attempts_key = f"{LOGIN_ATTEMPTS_KEY}_{username}"
    attempts = st.session_state.get(attempts_key, 0) + 1
    st.session_state[attempts_key] = attempts
    
    if attempts >= MAX_ATTEMPTS:
        # Blochează contul
        block_until = datetime.now() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        st.session_state[f"blocked_until_{username}"] = block_until
        # Resetează contorul (blocarea ține singură)
        st.session_state[attempts_key] = 0
        return True  # a fost blocat
    return False  # doar o încercare eșuată, încă neblocat

# ========== RESETEAZĂ BLOCARE (pentru Admin) ==========
def unblock_user(username):
    """Deblochează un utilizator (doar Admin)"""
    if f"blocked_until_{username}" in st.session_state:
        del st.session_state[f"blocked_until_{username}"]
    st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0

# ========== VERIFICĂ PIN ==========
def verify_pin(username, pin_input):
    """Verifică PIN-ul introdus"""
    pins = load_pins()
    
    # Verifică dacă există utilizatorul
    if username not in pins:
        return False
    
    # Hash-uiește PIN-ul introdus
    pin_hash = hashlib.sha256(pin_input.encode()).hexdigest()
    
    # Compară cu hash-ul stocat
    return pin_hash == pins[username]

# ========== SCHIMBĂ PIN (pentru Admin) ==========
def change_pin(username, new_pin):
    """Schimbă PIN-ul unui utilizator (doar Admin)"""
    pins = load_pins()
    if username not in pins:
        return False
    
    pins[username] = hashlib.sha256(new_pin.encode()).hexdigest()
    save_pins(pins)
    return True

# ========== FUNCȚIA PRINCIPALĂ – APELATĂ DIN APP.PY ==========
def verify_2fa(username):
    """
    Verifică al doilea factor (PIN)
    Returnează True dacă 2FA e trecut, False dacă nu
    Folosește st.session_state pentru a menține starea între rerun-uri
    """
    
    # Inițializează session state pentru 2FA
    if "2fa_passed" not in st.session_state:
        st.session_state["2fa_passed"] = False
    if "2fa_username" not in st.session_state:
        st.session_state["2fa_username"] = None
    
    # Dacă e deja autentificat 2FA pentru acest user, trece mai departe
    if st.session_state["2fa_passed"] and st.session_state["2fa_username"] == username:
        return True
    
    # Verifică blocarea
    if is_blocked(username):
        block_until = st.session_state[f"blocked_until_{username}"]
        minutes_left = int((block_until - datetime.now()).total_seconds() / 60) + 1
        st.error(f"🚫 Cont blocat temporar. Încearcă din nou peste {minutes_left} minute.")
        return False
    
    # Afișează interfața PIN
    st.markdown("---")
    st.subheader("🔐 Verificare securitate")
    
    pin_input = st.text_input(
        "Introdu codul PIN (primit pe WhatsApp)", 
        type="password", 
        max_chars=6,
        key=f"pin_input_{username}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
if st.button("✅ Verifică", key="verify_pin_btn", use_container_width=True):
    # Validare lungime
    if len(pin_input) != 6 or not pin_input.isdigit():
        st.warning("⚠️ PIN invalid. Trebuie să fie exact 6 cifre.")
        st.rerun()
    
    if verify_pin(username, pin_input):
        st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0
        st.success("✅ Cod corect!")
        return True
    else:
        was_blocked = register_failed_attempt(username)
        remaining = MAX_ATTEMPTS - st.session_state.get(f"{LOGIN_ATTEMPTS_KEY}_{username}", 1)
        
        if was_blocked:
            st.error(f"🚫 Prea multe încercări eșuate! Cont blocat {BLOCK_DURATION_MINUTES} minute.")
        else:
            st.error(f"❌ Cod incorect! Mai ai {remaining} încercări.")
        
        return False
    
    with col2:
        if st.button("◀️ Înapoi", key="back_to_login_btn", use_container_width=True):
            # Resetează tot și trimite înapoi la login
            st.session_state["authenticated"] = False
            st.session_state["2fa_passed"] = False
            st.rerun()
    
    return False


# ========== FUNCȚIE PENTRU ADMIN – AFIȘEAZĂ STAREA ==========
def show_admin_panel():
    """Afișează un mic panel în sidebar pentru Admin (opțional)"""
    if st.session_state.get("role") != "admin":
        return
    
    with st.sidebar.expander("🔧 Admin 2FA"):
        st.write("**Utilizatori blocați temporar:**")
        blocked_users = []
        for key in st.session_state.keys():
            if key.startswith("blocked_until_"):
                username = key.replace("blocked_until_", "")
                if is_blocked(username):
                    blocked_users.append(username)
        
        if blocked_users:
            for user in blocked_users:
                col1, col2 = st.columns([3, 1])
                col1.write(f"🚫 {user}")
                if col2.button("Deblochează", key=f"unblock_{user}"):
                    unblock_user(user)
                    st.success(f"{user} deblocat!")
                    st.rerun()
        else:
            st.write("Niciun utilizator blocat.")
        
        st.write("---")
        st.write("**Schimbă PIN utilizator:**")
        users = list(load_pins().keys())
        selected_user = st.selectbox("Utilizator", users, key="pin_user_select")
        new_pin = st.text_input("PIN nou (6 cifre)", max_chars=6, type="password", key="new_pin_input")
        if st.button("Schimbă PIN", key="change_pin_btn"):
            if new_pin and len(new_pin) == 6 and new_pin.isdigit():
                change_pin(selected_user, new_pin)
                st.success(f"PIN schimbat pentru {selected_user}!")
            else:
                st.error("PIN invalid. Trebuie să fie 6 cifre.")
