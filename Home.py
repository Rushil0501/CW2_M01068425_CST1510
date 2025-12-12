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
        st.markdown("### 🔐 Manual Login")
        
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
        
        st.markdown("---")
        
        # Demo Accounts Section - Dropdown Menu
        st.markdown("### 🎯 Demo Accounts")
        st.markdown(
            "<div style='background: rgba(255,20,147,0.1); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,20,147,0.3); margin-bottom: 20px;'>"
            "<p style='color: #FF1493; font-size: 14px; margin-bottom: 10px;'>"
            "Try the platform with these pre-configured demo accounts. Select an account from the dropdown below:</p>"
            "</div>",
            unsafe_allow_html=True
        )
        
        demo_accounts = [
            ("", "", "", "Select a demo account..."),
            ("Rushil_Cyber", "SecurePass123", "cyber", "🔒 Cybersecurity Dashboard"),
            ("Rushil_Data", "SecurePass123", "data", "📊 Data Science Dashboard"),
            ("Rushil_IT", "SecurePass123", "it", "💻 IT Operations Dashboard"),
        ]
        
        # Create dropdown options
        demo_options = [acc[3] for acc in demo_accounts]
        selected_demo = st.selectbox(
            "Choose a demo account to login:",
            demo_options,
            key="demo_account_selector"
        )
        
        # Find selected account
        selected_account = None
        for acc in demo_accounts:
            if acc[3] == selected_demo and acc[0]:  # Skip the placeholder
                selected_account = acc
                break
        
        # Display account info and login button
        if selected_account:
            username, password, role, label = selected_account
            st.markdown(
                f"<div style='padding: 10px; margin: 10px 0; background: rgba(255,20,147,0.05); border-radius: 8px;'>"
                f"<strong style='color: #FF1493;'>{label}</strong><br>"
                f"<span style='color: rgba(255,255,255,0.7); font-size: 12px;'>Username: <code style='background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;'>{username}</code> | "
                f"Password: <code style='background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;'>SecurePass123</code></span>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            if st.button("🚀 Login with Selected Account", key="demo_login_button"):
                success, msg, token, user_role = login_user(username, password)
                if success:
                    st.query_params = {
                        "user": [username],
                        "role": [user_role],
                    }
                    st.session_state.token = token
                    st.session_state.last_page = "Home"
                    self.launch_dashboard(user_role)
                else:
                    st.error(f"Demo login failed: {msg}")

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
                # Validate all fields are filled
                if not new_user or not new_pass or not conf_pass:
                    st.error("All fields are required.")
                    return

                # Validate password length
                if len(new_pass) < 3:
                    st.error("Password must be at least 3 characters long.")
                    return

                # Validate passwords match
                if new_pass != conf_pass:
                    st.error("Passwords do not match. Please try again.")
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
                    st.success("Account created successfully! Please switch to the Login tab.")
                else:
                    st.error(msg)


# Entry point
HomePage().render()
