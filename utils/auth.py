import uuid
import datetime
import streamlit as st
import json
import os
import hashlib

USER_DB_FILE = "users.json"
SESSION_DB_FILE = "sessions.json"

def _load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ... (Previous user logic remains) ...

def _load_sessions():
    if not os.path.exists(SESSION_DB_FILE):
        return {}
    try:
        with open(SESSION_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_sessions(sessions):
    with open(SESSION_DB_FILE, "w") as f:
        json.dump(sessions, f, indent=4)

def create_session_token(username):
    """Generates a token, saves it, and returns it."""
    token = str(uuid.uuid4())
    sessions = _load_sessions()
    sessions[token] = {
        "username": username,
        "created_at": str(datetime.datetime.now())
    }
    _save_sessions(sessions)
    return token

def get_user_from_token(token):
    """Validates token and returns username if valid."""
    sessions = _load_sessions()
    if token in sessions:
        return sessions[token]["username"]
    return None

def logout_token(token):
    """Removes token from sessions."""
    sessions = _load_sessions()
    if token in sessions:
        del sessions[token]
        _save_sessions(sessions)

def login_user(identifier, password):
    """
    Login with either username or email.
    """
    users = _load_users()
    hashed = _hash_password(password)
    
    # 1. Try direct username match
    if identifier in users:
        if users[identifier]["password"] == hashed:
            val_name = users[identifier].get("name", identifier)
            return True, val_name, identifier # Return actual username too
            
    # 2. Try email match (iterate)
    for u_user, u_data in users.items():
        if u_data.get("email") == identifier and u_data.get("password") == hashed:
            return True, u_data.get("name", u_user), u_user
            
    return False, None, None

def register_user(username, password, name, email):
    users = _load_users()
    if username in users:
        return False, "Username already exists."
    
    # Check if email exists
    for u_data in users.values():
        if u_data.get("email") == email:
            return False, "Email already exists."
    
    users[username] = {
        "password": _hash_password(password),
        "name": name,
        "email": email
    }
    _save_users(users)
    return True, "Registration successful! You can now login."

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_display_name = None
