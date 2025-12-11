import streamlit as st
from app.services.user_service import login_user, register_user
from app.ui.styles import load_custom_css


class HomePage:
    def __init__(self):
        st.set_page_config(
            page_title="Multi-Domain Intelligence Platform",
            page_icon="</>",
            layout="centered"
        )
        load_custom_css()

        if "token" not in st.session_state:
            st.session_state["token"] = ""

        self.qp = st.query_params

    def render(self):
        title_html = """
        <div class="neon-title-container">
            <span class="neon-logo"></></span> Multi-Domain Intelligence Platform
        </div>
        """
        st.markdown(title_html, unsafe_allow_html=True)

        self.quick_launch()
        self.render_auth_tabs()

    def quick_launch(self):
        if "user" in self.qp and self.qp.get("user"):
            username = self.qp.get("user")[0]
            role = self.qp.get("role", [""])[0]

            st.success(f"Welcome back — {username}")
            if st.button("🚀 Launch Dashboard"):
                st.session_state.last_page = "Home"
                self.launch_dashboard(role)

            st.markdown("---")

    def launch_dashboard(self, role):
        if role == "cyber":
            st.switch_page("pages/Cybersecurity.py")
        elif role == "it":
            st.switch_page("pages/IT_Operations.py")
        elif role == "data":
            st.switch_page("pages/Data_Science.py")
        else:
            st.info("No dashboard for this role.")

    def render_auth_tabs(self):
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            self.login_tab()
        with tab2:
            self.register_tab()

    def login_tab(self):
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Authenticate"):
                success, msg, token, role = login_user(username, password)

                if success:
                    st.query_params = {
                        "user": [username],
                        "role": [role],
                    }
                    st.session_state.token = token
                    st.session_state.last_page = "Home"
                    self.launch_dashboard(role)
                else:
                    st.error(msg)

    def register_tab(self):
        with st.form("register_form"):
            new_user = st.text_input("Username", key="reg_user")
            new_pass = st.text_input(
                "Password", type="password", key="reg_pass")
            conf_pass = st.text_input(
                "Confirm Password", type="password", key="reg_conf"
            )

            role_label = st.selectbox(
                "Department",
                [
                    "Cyber Security Analyst",
                    "Data Scientist",
                    "IT Support Specialist",
                ],
            )

            if st.form_submit_button("Create ID"):
                if not new_user or not new_pass or not conf_pass:
                    st.error("Fields missing.")
                    return

                if new_pass != conf_pass:
                    st.error("Passwords do not match.")
                    return

                role_map = {
                    "Cyber Security Analyst": "cyber",
                    "Data Scientist": "data",
                    "IT Support Specialist": "it",
                }

                success, msg = register_user(
                    new_user, new_pass, role_map[role_label]
                )

                if success:
                    st.success("Created! Switch to Login.")
                else:
                    st.error(msg)


# Entry point
HomePage().render()
