import streamlit as st


def load_custom_css():
    """Load global neon UI styling across all pages."""

    st.markdown(
        """
        <style>

        /* GLOBAL APP BACKGROUND */
        .stApp {
            background-color: #000000 !important;
            background-image: radial-gradient(circle at 50% 120%, rgba(255,20,147,0.45), #000000 60%);
            background-attachment: fixed;
        }

        /* TOP RIGHT PROFILE BAR */
        .profile-container {
            position: absolute;
            top: 15px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 6px 10px;
            background: rgba(255,255,255,0.07);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(8px);
        }

        .profile-name {
            color: #fff;
            font-weight: 600;
            font-size: 14px;
        }

        .profile-pic {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #FF1493;
        }

        .logout-btn {
            color: #FF1493 !important;
            font-size: 13px;
            font-weight: bold;
            text-decoration: none !important;
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid rgba(255,20,147,0.4);
        }

        /* CARDS / BOXES */
        .stCard, div[data-testid="stForm"], div[data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255,20,147,0.25) !important;
            box-shadow: 0 0 20px rgba(255,20,147,0.25) !important;
            border-radius: 14px !important;
            padding: 18px !important;
            backdrop-filter: blur(10px);
        }

        /* BUTTONS */
        div.stButton > button {
            background: linear-gradient(90deg, #FF1493, #C71585);
            color: white !important;
            border: none;
            padding: 10px 18px;
            border-radius: 10px;
            font-weight: bold;
            box-shadow: 0 0 12px rgba(255,20,147,0.6);
            transition: 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 18px rgba(255,20,147,0.95);
        }

        /* TEXT INPUT */
        .stTextInput input {
            background: rgba(255,255,255,0.1) !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }

        /* TABLES (TRANSLUCENT CSV DATA) */
        .dataframe {
            background: rgba(255,255,255,0.03) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(6px);
        }

        /* AI CHAT BOX */
        .ai-box {
            background: rgba(255,255,255,0.05);
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255,20,147,0.4);
            margin-top: 10px;
        }

        .ai-user {
            color: #FF1493;
            font-weight: bold;
        }

        .ai-bot {
            color: #9be7ff;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
