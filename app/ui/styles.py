import streamlit as st


def load_custom_css():
    """Load neon UI styling and layout overrides."""

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

        @keyframes ultra-smooth-fade {
            0% {
                background-position: 0% 0%; 
                opacity: 0.90; 
            }
            50% {
                background-position: 100% 100%; 
                opacity: 1;
            }
            100% {
                background-position: 0% 0%;
                opacity: 0.90;
            }
        }

        .stApp {
            background-color: #000000 !important;
            background-image: radial-gradient(circle at 50% 120%, rgba(255,20,147,0.45), #000000 60%);
            background-size: 500% 500%; 
            animation: ultra-smooth-fade 10s ease-in-out infinite alternate;
            background-attachment: fixed;
            will-change: background-position, opacity; 
        }

        .neon-title-container {
            font-family: 'Playfair Display', Georgia, serif; 
            color: #FF1493; 
            
            display: flex;
            justify-content: center;
            align-items: center;
            
            text-shadow: 
                0 0 4px #FF1493,
                0 0 6px #FF1493,
                0 0 10px rgba(255,20,147,0.6),
                0 0 20px rgba(255,20,147,0.4);
            
            font-size: 40px; 
            font-weight: 700; 
            margin-bottom: 30px;
            text-transform: none; 
        }

        div[data-testid="stText"] > div {
            display: flex !important;
            justify-content: center !important;
            width: 100%;
        }
        
        .neon-logo {
            font-size: 1.2em; 
            font-weight: 900;
            
            text-shadow: 
                0 0 5px #FFFFFF, 	
                0 0 10px #FF1493, 	
                0 0 25px #FF1493, 	
                0 0 60px rgba(255,20,147,0.9);
            
            color: #FFFFFF;
            margin-right: 15px;
            margin-left: -5px;
            
            animation: logo-pulse 3s infinite alternate ease-in-out;
        }

        @keyframes logo-pulse {
            0% { opacity: 0.9; }
            100% { opacity: 1.0; }
        }

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

        .stCard, div[data-testid="stForm"], div[data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255,20,147,0.25) !important;
            box-shadow: 0 0 20px rgba(255,20,147,0.25) !important;
            border-radius: 14px !important;
            padding: 18px !important;
            backdrop-filter: blur(10px);
        }

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

        .stTextInput input {
            background: rgba(255,255,255,0.1) !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }

        div[data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255,20,147,0.25) !important;
            box-shadow: 0 0 20px rgba(255,20,147,0.25) !important;
            border-radius: 14px !important;
            padding: 0px !important;
            backdrop-filter: blur(10px);
            overflow: hidden; 
        }
        
        div[data-testid="stDataFrame"] .ag-header-cell,
        div[data-testid="stDataFrame"] .ag-row {
            background: transparent !important; 
        }
        
        div[data-testid="stDataFrame"] .ag-cell,
        div[data-testid="stDataFrame"] .ag-header-cell-label {
            color: #FFFFFF !important;
        }
        
        div[data-testid="stDataFrame"] .ag-root-wrapper,
        div[data-testid="stDataFrame"] .ag-cell,
        div[data-testid="stDataFrame"] .ag-header-cell {
            border-color: rgba(255,255,255,0.1) !important;
        }


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
        
        .ai-chat-bubble-user {
            background: rgba(255, 20, 147, 0.2); 
            padding: 10px;
            border-radius: 12px;
            border-bottom-right-radius: 0;
            margin-bottom: 5px;
            color: white;
            font-size: 14px;
        }
        
        .ai-chat-bubble-assistant {
            background: rgba(155, 231, 255, 0.15); 
            padding: 10px;
            border-radius: 12px;
            border-bottom-left-radius: 0;
            margin-bottom: 5px;
            color: white;
            font-size: 14px;
        }
        
        @keyframes typing-dot {
            0%, 60%, 100% { 
                opacity: 0.3; 
                transform: translateY(0);
            }
            30% { 
                opacity: 1; 
                transform: translateY(-3px);
            }
        }
        
        .typing-dots {
            display: inline-block;
            margin-left: 3px;
        }
        
        .typing-dots span {
            display: inline-block;
            animation: typing-dot 1.4s infinite;
            margin: 0 1px;
        }
        
        .typing-dots span:nth-child(1) {
            animation-delay: 0s;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        .ai-response {
            background: rgba(155, 231, 255, 0.15); 
            padding: 10px;
            border-radius: 12px;
            border-bottom-left-radius: 0;
            margin-bottom: 5px;
            color: white;
            font-size: 14px;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )
