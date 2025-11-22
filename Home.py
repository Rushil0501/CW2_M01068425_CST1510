import streamlit as st
from app.services.user_service import login_user, register_user

# Page Configuration
st.set_page_config(page_title="Login - Intelligence Platform",
                   page_icon="🔐", layout="centered")

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Multi-Domain Intelligence Platform")

# If already logged in, redirect (or show button)
if st.session_state.logged_in:
    st.success(f"Currently logged in as: **{st.session_state.username}**")
    if st.button("Go to Dashboard", type="primary"):
        st.switch_page("pages/Dashboard.py")
    st.stop()

# Tabs for Login and Register
tab1, tab2 = st.tabs(["Login", "Register"])

# --- LOGIN TAB ---
with tab1:
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Log In", type="primary")

    if submit_login:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            # Call your backend function from Week 8
            success, msg = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(msg)
                # Navigate to the dashboard
                st.switch_page("pages/Dashboard.py")
            else:
                st.error(msg)

# --- REGISTER TAB ---
with tab2:
    st.header("Register")
    with st.form("register_form"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        # Optional: Add Role selection if you want (default is user)
        submit_register = st.form_submit_button("Create Account")

    if submit_register:
        if not new_user or not new_pass:
            st.error("Please fill in all fields.")
        else:
            # Call your backend function from Week 8
            success, msg = register_user(new_user, new_pass)
            if success:
                st.success(msg + " Please switch to the Login tab to sign in.")
            else:
                st.error(msg)
