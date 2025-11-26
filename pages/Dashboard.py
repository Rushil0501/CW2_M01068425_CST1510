import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import DB Functions
from app.data.incidents import get_all_incidents, insert_incident
from app.data.tickets import get_all_tickets, insert_ticket
from app.data.datasets import list_datasets, load_csv_to_table

# Import AI Service
from app.services.ai_service import get_gemini_response

# 1. Page Config
st.set_page_config(page_title="Multi-Domain Intelligence Platform",
                   layout="wide", page_icon="</>")

# 2. Visuals & CSS


def set_visuals():
    st.markdown("""
        <style>
        /* HIDE DEFAULT NAV */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        
        /* BACKGROUND */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 100%, rgba(255, 20, 147, 0.4) 0%, rgba(0, 0, 0, 1) 60%);
            background-attachment: fixed;
        }
        
        /* TOP NAV BAR CONTAINER */
        .nav-container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,20,147,0.3);
            padding: 15px;
            margin-bottom: 20px;
        }

        /* GLOWING BUTTONS */
        div.stButton > button {
            background: linear-gradient(90deg, #FF1493, #C71585);
            color: white;
            border: none;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(255, 20, 147, 0.4);
            font-weight: bold;
            font-size: 16px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 20, 147, 0.8);
        }
        
        /* PROFILE BADGE STYLING */
        .profile-container {
            background: rgba(20, 20, 20, 0.8);
            border: 1px solid #FF1493;
            border-radius: 12px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.3);
            backdrop-filter: blur(10px);
            width: fit-content;
            margin-left: auto;
        }
        
        /* --- CHANGED: Emoji Glow Effect --- */
        .profile-icon {
            font-size: 32px;
            /* White drop-shadow creates a 'backlit' glow that enhances the emoji's natural colors */
            filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.6));
        }
        
        .profile-text-col {
            display: flex;
            flex-direction: column;
            line-height: 1.3;
        }
        
        .profile-name {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(255,255,255,0.3);
        }
        
        .profile-role {
            color: #FF1493;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }

        /* DASHBOARD CONTAINERS */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 20, 147, 0.2);
            border-radius: 10px;
            backdrop-filter: blur(5px);
        }
        
        /* INPUT FORM STYLING */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
            color: white !important;
            border: 1px solid #555;
        }
        </style>
    """, unsafe_allow_html=True)


set_visuals()

# ---------------------------------------------------------
# CHART HELPER
# ---------------------------------------------------------


def render_aesthetic_chart(df, x_col, color_col, title, chart_type="bar"):
    neon_colors = ["#FF1493", "#00F0FF",
                   "#FFD700", "#ADFF2F", "#FF4500", "#9400D3"]

    if chart_type == "bar":
        fig = px.bar(
            df, x=x_col, color=color_col,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=neon_colors,
            barmode='group'
        )
        fig.update_traces(marker_line_width=0, opacity=0.9)

    elif chart_type == "pie":
        fig = px.pie(
            df, names=x_col,
            title=title,
            template="plotly_dark",
            hole=0.6,
            color_discrete_sequence=neon_colors
        )
        fig.update_traces(textinfo='percent+label',
                          marker=dict(line=dict(color='#000000', width=2)))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=14, color="#E0E0E0"),
        title_font=dict(size=18, family="sans-serif", color="#FF1493"),
        xaxis=dict(showgrid=False, title="", showticklabels=True),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title=""),
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)


# 3. Security Guard
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()

role = st.session_state.role
user = st.session_state.username

# ---------------------------------------------------------
# 4. TOP NAVIGATION
# ---------------------------------------------------------
with st.container():
    c1, c2, c3 = st.columns([5, 4, 1.5])

    with c1:
        if role == 'cyber':
            title = "🕵️‍♂️ CYBER OPS"
        elif role == 'it':
            title = "🛠️ IT SUPPORT"
        elif role == 'data':
            title = "🧠 DATA LAB"
        else:
            title = "⚡ ADMIN PANEL"

        st.markdown(f"""
            <h1 style='margin:0; padding:0; font-size: 36px; 
            background: linear-gradient(90deg, #FFFFFF, #FF1493); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 5px rgba(255,20,147,0.5));'>
            {title}
            </h1>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="profile-container">
                <div class="profile-icon">👤</div>
                <div class="profile-text-col">
                    <span class="profile-name">{user}</span>
                    <span class="profile-role">{role.upper()}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown('<div style="margin-top: 5px;"></div>',
                    unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.switch_page("Home.py")

st.markdown("---")

# ---------------------------------------------------------
# 5. MAIN CONTENT
# ---------------------------------------------------------

# === CYBER ===
if role == "cyber" or role == "admin":
    df = get_all_incidents()

    m1, m2, m3 = st.columns(3)
    m1.metric("Incidents", len(df))
    m2.metric("Critical", len(df[df['severity'] == 'Critical']))
    m3.metric("Open", len(df[df['status'] == 'Open']))

    c1, c2 = st.columns(2)
    with c1:
        if not df.empty:
            render_aesthetic_chart(
                df, 'category', 'severity', "Incidents by Category", "bar")

    with c2:
        st.dataframe(df, use_container_width=True, height=350)

    with st.container(border=True):
        st.subheader("🚨 Report Incident")
        with st.form("cyber"):
            cat = st.selectbox("Type", ["Phishing", "Malware", "DDoS"])
            sev = st.selectbox("Severity", ["High", "Critical"])
            desc = st.text_area("Description")
            if st.form_submit_button("Submit Report"):
                insert_incident(str(datetime.now()), sev, cat, "Open", desc)
                st.success("Reported.")
                st.rerun()

# === IT SUPPORT ===
elif role == "it":
    df_tickets = get_all_tickets()

    k1, k2 = st.columns(2)
    k1.metric("Total Tickets", len(df_tickets))
    k2.metric("Pending", len(df_tickets[df_tickets['status'] == 'Pending']))

    st.dataframe(df_tickets, use_container_width=True)

    if not df_tickets.empty:
        render_aesthetic_chart(df_tickets, 'priority',
                               'status', "Ticket Priority Distribution", "bar")

    with st.container(border=True):
        st.subheader("➕ New Ticket")
        with st.form("it"):
            p = st.selectbox("Priority", ["Low", "High"])
            d = st.text_input("Issue")
            if st.form_submit_button("Create Ticket"):
                insert_ticket(p, d, "Pending", "Admin", str(datetime.now()), 0)
                st.success("Created.")
                st.rerun()

# === DATA ===
elif role == "data":
    df_data = list_datasets()

    st.metric("Datasets", len(df_data))
    st.dataframe(df_data, use_container_width=True)

    if not df_data.empty:
        render_aesthetic_chart(df_data, 'name', 'rows',
                               "Dataset Sizes (Rows)", "bar")

    with st.container(border=True):
        st.subheader("📤 Upload Dataset")
        f = st.file_uploader("CSV File", type="csv")
        if f and st.button("Upload"):
            path = f"DATA/{f.name}"
            with open(path, "wb") as file:
                file.write(f.getbuffer())
            load_csv_to_table(path, f.name.split('.')[0], 'replace')
            st.success("Uploaded.")
            st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# 6. AI COMMAND CONSOLE
# ---------------------------------------------------------

if role == 'cyber':
    ai_name = "🕵️‍♂️ CYBER OPS AI"
elif role == 'it':
    ai_name = "🛠️ IT SUPPORT AI"
elif role == 'data':
    ai_name = "🧠 DATA LAB AI"
else:
    ai_name = "⚡ ADMIN AI"

st.subheader(ai_name)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Scrollable Chat History
chat_container = st.container(height=400, border=True)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Static Input Form
with st.form(key="ai_chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([8, 1])

    with col_input:
        user_prompt = st.text_input(
            "Message", placeholder=f"Ask {ai_name}...", label_visibility="collapsed")

    with col_btn:
        submitted = st.form_submit_button("🚀")

    if submitted and user_prompt:
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_prompt)

        st.session_state.messages.append(
            {"role": "user", "content": user_prompt})

        with chat_container:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                try:
                    stream = get_gemini_response(
                        user_prompt, st.session_state.messages, role)
                    for chunk in stream:
                        try:
                            if chunk.text:
                                full_response += chunk.text
                                response_placeholder.markdown(
                                    full_response + "▌")
                        except ValueError:
                            pass
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"AI Error: {e}")
