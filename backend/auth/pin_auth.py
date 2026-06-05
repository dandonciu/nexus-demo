"""
Modul 2FA simplu cu PIN fix + blocare dupa 3 incercari
FARA fisier JSON - PIN-uri direct in cod
"""

import streamlit as st
import hashlib
from datetime import datetime, timedelta

# ========== CONFIGURARE ==========
LOGIN_ATTEMPTS_KEY = "pin_failed_attempts"
BLOCK_DURATION_MINUTES = 15
MAX_ATTEMPTS = 3

# ========== PIN-URI DIRECT IN COD ==========
# Modifica aici PIN-urile pentru fiecare utilizator
PIN_URI = {
    "angajat": hashlib.sha256("111111".encode()).hexdigest(),
    "manager": hashlib.sha256("123456".encode()).hexdigest(),
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
        st.error(f"❌ Cont blocat temporar. Incercati din nou peste {minutes_left} minute.")
        if st.button("◀️ Înapoi la autentificare", key="back_from_blocked"):
            st.session_state.awaiting_2fa = False
            st.session_state.pending_2fa_user = None
            st.rerun()
        return False
    
    # Container centrat pentru 2FA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>🔐 Verificare cod securitate</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>Utilizator: <b>{username}</b></p>", unsafe_allow_html=True)
        
        # Afișează câte încercări au rămas
        attempts_used = st.session_state.get(f"{LOGIN_ATTEMPTS_KEY}_{username}", 0)
        remaining = MAX_ATTEMPTS - attempts_used
        if remaining > 0 and remaining < MAX_ATTEMPTS:
            st.warning(f"⚠️ Mai ai {remaining} încercări rămase.")
        
        with st.form(key=f"2fa_form_{username}"):
            pin_input = st.text_input("Cod PIN (6 cifre)", type="password", max_chars=6, placeholder="PIN", label_visibility="collapsed")
            submitted = st.form_submit_button("✅ Verifică", use_container_width=True)
            
            if submitted:
                if not pin_input:
                    st.warning("Introdu codul PIN")
                    st.rerun()
                if len(pin_input) != 6 or not pin_input.isdigit():
                    st.warning("PIN invalid. Trebuie să fie exact 6 cifre.")
                    st.rerun()
                if verify_pin(username, pin_input):
                    # Reset succes
                    st.session_state[f"{LOGIN_ATTEMPTS_KEY}_{username}"] = 0
                    st.success("✅ Cod corect!")
                    return True
                else:
                    was_blocked = register_failed_attempt(username)
                    remaining_after = MAX_ATTEMPTS - st.session_state.get(f"{LOGIN_ATTEMPTS_KEY}_{username}", 0)
                    if was_blocked:
                        st.error(f"❌ Prea multe încercări eșuate! Cont blocat {BLOCK_DURATION_MINUTES} minute.")
                        if st.button("◀️ Înapoi la autentificare", key="back_after_block"):
                            st.session_state.awaiting_2fa = False
                            st.session_state.pending_2fa_user = None
                            st.rerun()
                    else:
                        st.error(f"❌ Cod incorect! Mai ai {remaining_after} încercări.")
                    return False
        
        # Buton Înapoi - mereu vizibil
        st.markdown("---")
        if st.button("◀️ Înapoi la autentificare", key="back_to_login_main", use_container_width=True):
            st.session_state.awaiting_2fa = False
            st.session_state.pending_2fa_user = None
            st.rerun()
    
    return False

