"""
Modul 2FA simplu cu PIN fix + blocare dupa 3 incercari
FARA fisier JSON - PIN-uri direct in cod
"""

import streamlit as st
import hashlib
from datetime import datetime, timedelta

# ========== CONFIGURARE ==========
LOGIN_ATTEMPTS_KEY = "pin_failed_attempts"
BLOCK_DURATION_MINUTES = 30
MAX_ATTEMPTS = 3

# ========== PIN-URI DIRECT IN COD ==========
# Modifica aici PIN-urile pentru fiecare utilizator
PIN_URI = {
    "angajat": hashlib.sha256("222222".encode()).hexdigest(),
    "manager": hashlib.sha256("222222".encode()).hexdigest(),
    "admin": hashlib.sha256("333333".encode()).hexdigest()
}

def is_blocked(username):
    if f"blocked_until_{username}" not in st.session_state:
        return False
    block_until = st.session_state[f"blocked_until_{username}"]
    if datetime.now() < block_until:
        return True
    del st.session_state[f"blocked_until_{username}"]
    st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0
    return False

def register_failed_attempt(username):
    attempts_key = f"{LOGIN_ATTEMPTS_KEY}_{username}"
    attempts = st.session_state.get(attempts_key, 0) + 1
    st.session_state[attempts_key] = attempts
    if attempts >= MAX_ATTEMPTS:
        block_until = datetime.now() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        st.session_state[f"blocked_until_{username}"] = block_until
        st.session_state[attempts_key] = 0
        return True
    return False

def unblock_user(username):
    if f"blocked_until_{username}" in st.session_state:
        del st.session_state[f"blocked_until_{username}"]
    st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0

def verify_pin(username, pin_input):
    if username not in PIN_URI:
        return False
    pin_hash = hashlib.sha256(pin_input.encode()).hexdigest()
    return pin_hash == PIN_URI[username]

def change_pin(username, new_pin):
    """Schimba PIN-ul in memorie (pierdut la restart)"""
    if username not in PIN_URI:
        return False
    PIN_URI[username] = hashlib.sha256(new_pin.encode()).hexdigest()
    return True

def verify_2fa(username):
    if st.session_state.get("logged_in", False):
        return True
    
    if is_blocked(username):
        block_until = st.session_state[f"blocked_until_{username}"]
        minutes_left = int((block_until - datetime.now()).total_seconds() / 60) + 1
        st.error(f"Cont blocat temporar. Incercati din nou peste {minutes_left} minute.")
        return False
    
    st.markdown("---")
    st.subheader("Verificare cod securitate")
    st.caption("Introdu codul PIN primit pe WhatsApp")
    
    pin_input = st.text_input("Cod PIN (6 cifre)", type="password", max_chars=6, key=f"pin_input_{username}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verifica", key="verify_pin_btn", use_container_width=True):
            if not pin_input:
                st.warning("Introdu codul PIN")
                st.rerun()
            if len(pin_input) != 6 or not pin_input.isdigit():
                st.warning("PIN invalid. Trebuie sa fie exact 6 cifre.")
                st.rerun()
            if verify_pin(username, pin_input):
                st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0
                st.success("Cod corect!")
                return True
            else:
                was_blocked = register_failed_attempt(username)
                remaining = MAX_ATTEMPTS - st.session_state.get(f"{LOGIN_ATTEMPTS_KEY}_{username}", 1)
                if was_blocked:
                    st.error(f"Prea multe incercari esuate! Cont blocat {BLOCK_DURATION_MINUTES} minute.")
                else:
                    st.error(f"Cod incorect! Mai ai {remaining} incercari.")
                return False
    
    with col2:
        if st.button("Inapoi", key="back_to_login_btn", use_container_width=True):
            st.session_state.awaiting_2fa = False
            st.session_state.pending_2fa_user = None
            st.rerun()
    
    return False

def admin_2fa_panel():
    if st.session_state.get("role") not in ["admin", "manager"]:
        return
    with st.sidebar.expander("Admin 2FA", expanded=False):
        blocked_users = []
        for key in st.session_state.keys():
            if key.startswith("blocked_until_"):
                username = key.replace("blocked_until_", "")
                if is_blocked(username):
                    blocked_users.append(username)
        if blocked_users:
            st.warning(f"Blocati: {', '.join(blocked_users)}")
            for user in blocked_users:
                if st.button(f"Deblocheaza {user}", key=f"unblock_{user}"):
                    unblock_user(user)
                    st.success(f"{user} deblocat!")
                    st.rerun()
        else:
            st.success("Niciun utilizator blocat")
