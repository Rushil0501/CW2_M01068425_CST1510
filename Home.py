import streamlit as st
from app.services.user_service import login_user, register_user

# 1. Page Config (UPDATED TITLE & LOGO)
st.set_page_config(page_title="Multi-Domain Intelligence Platform",
                   page_icon="</>", layout="centered")

# 2. Realistic CSS (Hidden Sidebar + Glowing Buttons + Footer)


def set_visuals():
    st.markdown("""
        <style>
        /* --- HIDE SIDEBAR --- */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}

        /* --- BACKGROUND --- */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 100%, rgba(255, 20, 147, 0.5) 0%, rgba(0, 0, 0, 1) 50%);
            background-attachment: fixed;
        }

        /* --- GLASS FORMS --- */
        div[data-testid="stForm"], div[data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 20, 147, 0.3);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            border-radius: 16px;
            padding: 20px;
        }

        /* --- REALISTIC GLOWING BUTTONS --- */
        div.stButton > button {
            background: linear-gradient(90deg, #FF1493, #C71585);
            color: white;
            border: none;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(255, 20, 147, 0.5); /* Pink Glow */
            transition: all 0.3s ease;
            font-weight: bold;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 20, 147, 0.9);
        }

        /* Text Inputs */
        .stTextInput input {
            background-color: rgba(0, 0, 0, 0.5) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            background: linear-gradient(90deg, #FF1493, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* --- FOOTER (RR 🍃) --- */
        .footer-signature {
            position: fixed;
            bottom: 10px;
            right: 15px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            font-family: monospace;
            background: rgba(0, 0, 0, 0.4);
            padding: 4px 8px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(2px);
            pointer-events: none; /* Let clicks pass through */
        }
        </style>
    """, unsafe_allow_html=True)

    # Inject the footer HTML
    st.markdown('<div class="footer-signature">RR 🍃</div>',
                unsafe_allow_html=True)


set_visuals()

# 3. Session Logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "token" not in st.session_state:
    st.session_state.token = ""

# UPDATED MAIN TITLE
st.title("</> Multi-Domain Intelligence Platform")

if st.session_state.logged_in:
    st.success(f"User: {st.session_state.username}")
    if st.button("🚀 Launch Dashboard"):
        st.switch_page("pages/Dashboard.py")
    st.stop()

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Authenticate"):
            success, msg, token, role = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = token
                st.session_state.role = role
                st.switch_page("pages/Dashboard.py")
            else:
                st.error(msg)

with tab2:
    with st.form("register_form"):
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        conf_pass = st.text_input("Confirm Password", type="password")
        role_label = st.selectbox("Department", [
                                  "Cyber Security Analyst", "Data Scientist", "IT Support Specialist"])

        if st.form_submit_button("Create ID"):
            if not new_user or not new_pass or not conf_pass:
                st.error("Fields missing.")
            elif new_pass != conf_pass:
                st.error("Passwords do not match.")
            else:
                role_map = {"Cyber Security Analyst": "cyber",
                            "Data Scientist": "data", "IT Support Specialist": "it"}
                success, msg = register_user(
                    new_user, new_pass, role=role_map[role_label])
                if success:
                    st.success("Created! Switch to Login.")
                else:
                    st.error(msg)
