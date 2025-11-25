import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import DB functions
from app.data.incidents import get_all_incidents, insert_incident
from app.data.tickets import get_all_tickets, insert_ticket
from app.data.datasets import list_datasets, load_csv_to_table

st.set_page_config(page_title="Department Dashboard", layout="wide")

# --- 1. AUTH & ROLE CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Access Denied")
    st.stop()

user_role = st.session_state.role  # e.g., 'cyber', 'it', 'data'
username = st.session_state.username

# --- 2. HEADER ---
st.title(f"Dashboard: {user_role.upper()} Department")
st.write(f"Logged in as: **{username}**")

# Logout button in sidebar
with st.sidebar:
    st.header(f"User: {username}")
    st.info(f"Role: {user_role}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.switch_page("Home.py")

# --- 3. CONDITIONAL RENDERING ---

# ==========================================
# VIEW 1: CYBER ANALYST (Restricted)
# ==========================================
if user_role == "cyber" or user_role == "admin":
    st.subheader("🛡️ Cyber Security Operations")

    df = get_all_incidents()

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", len(df))
    c2.metric("Critical", len(df[df['severity'] == 'Critical']))
    c3.metric("Open Cases", len(df[df['status'] == 'Open']))

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        if not df.empty:
            fig = px.bar(df, x='category', color='severity',
                         title="Incidents by Type")
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not df.empty:
            fig2 = px.pie(df, names='status', title="Status Breakdown")
            st.plotly_chart(fig2, use_container_width=True)

    # Submission Form (Cyber Only)
    with st.expander("🚨 Report Incident"):
        with st.form("cyber_report"):
            cat = st.selectbox("Category", ["Phishing", "Malware", "DDoS"])
            sev = st.selectbox("Severity", ["Low", "High", "Critical"])
            desc = st.text_area("Description")
            if st.form_submit_button("Submit"):
                insert_incident(str(datetime.now()), sev, cat, "Open", desc)
                st.success("Reported!")
                st.rerun()

# ==========================================
# VIEW 2: DATA SCIENTIST (Restricted)
# ==========================================
elif user_role == "data":
    st.subheader("📊 Data Science Hub")

    df_data = list_datasets()

    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("Available Datasets", len(df_data))
    m2.metric("Total Rows", df_data['rows'].sum() if not df_data.empty else 0)

    # Table
    st.dataframe(df_data, use_container_width=True)

    # Upload Tool (Data Only)
    st.markdown("### 📤 Upload New Dataset")
    up_file = st.file_uploader("Upload CSV", type="csv")
    if up_file:
        if st.button("Process Data"):
            path = f"DATA/{up_file.name}"
            with open(path, "wb") as f:
                f.write(up_file.getbuffer())
            load_csv_to_table(path, up_file.name.split('.')[0], 'replace')
            st.success("Dataset uploaded and registered.")
            st.rerun()

# ==========================================
# VIEW 3: IT SPECIALIST (Restricted)
# ==========================================
elif user_role == "it":
    st.subheader("🎫 IT Support Tickets")

    df_tickets = get_all_tickets()

    # Metrics
    t1, t2 = st.columns(2)
    t1.metric("Queue Depth", len(df_tickets))
    t2.metric("Unassigned", len(
        df_tickets[df_tickets['assigned_to'].isnull()]))

    # Visuals
    if not df_tickets.empty:
        fig = px.bar(df_tickets, x='priority',
                     color='status', title="Ticket Priority")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_tickets, use_container_width=True)

    # Ticket Creation (IT Only)
    with st.expander("➕ New Ticket"):
        with st.form("it_form"):
            prio = st.selectbox("Priority", ["Low", "Medium", "High"])
            desc = st.text_input("Issue")
            if st.form_submit_button("Create Ticket"):
                insert_ticket(prio, desc, "Open", "Unassigned",
                              str(datetime.now()), 0)
                st.success("Ticket created.")
                st.rerun()

# ==========================================
# FALLBACK
# ==========================================
else:
    st.error(f"Role '{user_role}' is not recognised. Please contact Admin.")
