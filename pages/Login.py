import streamlit as st
from app.services.user_service import login_user

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.title("🔐 Secure Login Portal")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    success, msg, token, role = login_user(username, password)

    if success:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.token = token
        st.session_state.messages = []

        # Redirect based on role
        if role == "cyber":
            st.switch_page("pages/Cybersecurity.py")
        elif role == "it":
            st.switch_page("pages/IT_Operations.py")
        elif role == "data":
            st.switch_page("pages/Data_Science.py")
        else:
            st.switch_page("pages/AI_Assistant.py")

    else:
        st.error(msg)
