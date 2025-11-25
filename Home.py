import streamlit as st
from app.services.user_service import login_user, register_user

st.set_page_config(page_title="Login - Intelligence Platform",
                   page_icon="🔐", layout="centered")

# Initialise Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "token" not in st.session_state:
    st.session_state.token = ""

st.title("🔐 Multi-Domain Intelligence Platform")

if st.session_state.logged_in:
    st.success(
        f"Welcome back, **{st.session_state.username}** ({st.session_state.role})")
    if st.button("Go to Dashboard", type="primary"):
        st.switch_page("pages/Dashboard.py")
    st.stop()

tab1, tab2 = st.tabs(["Login", "Register"])

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
            # UPDATED CALL: Expecting 4 return values now
            success, msg, token, role = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = token
                st.session_state.role = role
                st.success(f"{msg} Redirecting...")
                st.switch_page("pages/Dashboard.py")
            else:
                st.error(msg)

with tab2:
    st.header("Register")
    with st.form("register_form"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        # Optional: Allow selecting role for demo purposes
        new_role = st.selectbox("Select Role", ["user", "analyst", "admin"])
        submit_register = st.form_submit_button("Create Account")

    if submit_register:
        if not new_user or not new_pass:
            st.error("Please fill in all fields.")
        else:
            # Pass the selected role to register_user
            success, msg = register_user(new_user, new_pass, role=new_role)
            if success:
                st.success(msg + " Please switch to Login tab.")
            else:
                st.error(msg)
