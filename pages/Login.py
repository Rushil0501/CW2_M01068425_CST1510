import streamlit as st
from app.services.user_service import login_user


class LoginPage:
    def __init__(self):
        st.set_page_config(page_title="Login",
                           page_icon="🔐", layout="centered")
        st.title("🔐 Secure Login Portal")
        self.username = None
        self.password = None

    def render_form(self):
        self.username = st.text_input("Username")
        self.password = st.text_input("Password", type="password")

        if st.button("Login"):
            self.handle_login()

    def handle_login(self):
        success, msg, token, role = login_user(
            self.username, self.password)

        if success:
            st.session_state.logged_in = True
            st.session_state.username = self.username
            st.session_state.role = role
            st.session_state.token = token
            st.session_state.messages = []

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

    def run(self):
        self.render_form()


if __name__ == "__main__":
    LoginPage().run()
