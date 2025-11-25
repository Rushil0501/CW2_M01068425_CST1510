import streamlit as st
from app.services.user_service import login_user, register_user

st.set_page_config(page_title="Login Portal", page_icon="🔐", layout="centered")

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""  # We will store 'cyber', 'data', or 'it' here

st.title("🔐 Enterprise Portal")

# Redirect if logged in
if st.session_state.logged_in:
    st.success(
        f"Logged in as {st.session_state.username} ({st.session_state.role})")
    if st.button("Go to My Dashboard", type="primary"):
        st.switch_page("pages/Dashboard.py")
    st.stop()

tab1, tab2 = st.tabs(["Login", "Register"])

# --- LOGIN TAB ---
with tab1:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Log In", type="primary")

    if submit_login:
        # Expect 4 return values now
        success, msg, token, role = login_user(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.token = token
            st.session_state.role = role  # Save role to session
            st.success("Login successful! Redirecting...")
            st.switch_page("pages/Dashboard.py")
        else:
            st.error(msg)

# --- REGISTER TAB ---
with tab2:
    st.info("New accounts must be assigned to a specific department.")
    with st.form("register_form"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")

        # STRICT ROLE SELECTION
        # We map friendly names to database codes
        role_options = {
            "Cyber Security Analyst": "cyber",
            "Data Scientist": "data",
            "IT Support Specialist": "it"
        }
        selected_label = st.selectbox(
            "Select Department", list(role_options.keys()))
        new_role = role_options[selected_label]

        submit_register = st.form_submit_button("Create Account")

    if submit_register:
        if not new_user or not new_pass:
            st.error("All fields are required.")
        else:
            # Pass the selected 'new_role' to the backend
            success, msg = register_user(new_user, new_pass, role=new_role)
            if success:
                st.success(
                    f"Account created for {selected_label}! Please log in.")
            else:
                st.error(msg)
