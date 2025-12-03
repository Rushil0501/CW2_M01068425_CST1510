import streamlit as st


def set_visuals():
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}

        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 100%, rgba(255, 20, 147, 0.5) 0%, rgba(0, 0, 0, 1) 50%);
            background-attachment: fixed;
        }

        div[data-testid="stForm"], div[data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 20, 147, 0.3);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            border-radius: 16px;
            padding: 20px;
        }

        div.stButton > button {
            background: linear-gradient(90deg, #FF1493, #C71585);
            color: white;
            border: none;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(255, 20, 147, 0.6);
            transition: all 0.3s ease;
            font-weight: bold;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 20, 147, 1);
        }

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
        </style>
    """, unsafe_allow_html=True)
