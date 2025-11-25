import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import DB functions
from app.data.incidents import get_all_incidents, insert_incident
from app.data.tickets import get_all_tickets, insert_ticket
from app.data.datasets import list_datasets, load_csv_to_table

st.set_page_config(page_title="Enterprise Dashboard",
                   layout="wide", page_icon="🏢")

# --- AUTH GUARD ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Access Denied. Please login.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# --- SIDEBAR & USER PROFILE ---
with st.sidebar:
    st.header("👤 User Profile")
    st.write(f"**User:** {st.session_state.username}")
    st.write(f"**Role:** `{st.session_state.role.upper()}`")

    # Display Session Token (masked for security, visible for verification)
    token_display = st.session_state.token[:6] + \
        "..." + st.session_state.token[-4:]
    st.code(token_display, language="text")
    st.caption("Session Active")

    st.divider()

    # Domain Navigation
    domain = st.radio("Select Domain", [
                      "🛡️ Cyber Security", "🎫 IT Support", "📊 Data Science"])

    st.divider()
    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.token = ""
        st.switch_page("Home.py")

st.title(f"{domain} Dashboard")

# ==========================================
# DOMAIN 1: CYBER SECURITY
# ==========================================
if domain == "🛡️ Cyber Security":
    # 1. Metrics
    df_cyber = get_all_incidents()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidents", len(df_cyber))
    col2.metric("Critical", len(df_cyber[df_cyber['severity'] == 'Critical']))
    col3.metric("Open Cases", len(df_cyber[df_cyber['status'] == 'Open']))

    # Role Check: Only Admin/Analyst sees sensitive High Severity count highlight
    if st.session_state.role in ['admin', 'analyst']:
        col4.metric("High Severity", len(
            df_cyber[df_cyber['severity'] == 'High']), delta="Priority")

    # 2. Visualization
    c1, c2 = st.columns(2)
    with c1:
        if not df_cyber.empty:
            fig = px.bar(df_cyber, x='category', color='severity',
                         title="Incidents by Category")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if not df_cyber.empty:
            fig2 = px.pie(df_cyber, names='status',
                          title="Current Status Distribution")
            st.plotly_chart(fig2, use_container_width=True)

    # 3. Data Table
    st.subheader("Live Incident Feed")
    st.dataframe(df_cyber, use_container_width=True)

    # 4. Action: Report Incident (Admins and Analysts only)
    if st.session_state.role in ['admin', 'analyst']:
        with st.expander("🚨 Report New Security Incident"):
            with st.form("cyber_form"):
                d_cat = st.selectbox(
                    "Category", ["Phishing", "Malware", "DDoS", "Insider"])
                d_sev = st.selectbox(
                    "Severity", ["Low", "Medium", "High", "Critical"])
                d_desc = st.text_area("Description")
                if st.form_submit_button("Submit Report"):
                    insert_incident(str(datetime.now()), d_sev,
                                    d_cat, "Open", d_desc)
                    st.success("Incident Logged")
                    st.rerun()

# ==========================================
# DOMAIN 2: IT SUPPORT TICKETS
# ==========================================
elif domain == "🎫 IT Support":
    df_tickets = get_all_tickets()

    # 1. Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tickets", len(df_tickets))
    m2.metric("Pending", len(df_tickets[df_tickets['status'] == 'Pending']))

    # Calculate avg resolution time
    avg_res = df_tickets['resolution_time_hours'].mean(
    ) if not df_tickets.empty else 0
    m3.metric("Avg Resolution (Hrs)", f"{avg_res:.1f}")

    # 2. Visuals
    if not df_tickets.empty:
        fig_tick = px.bar(df_tickets, x='priority', color='status',
                          barmode='group', title="Tickets by Priority")
        st.plotly_chart(fig_tick, use_container_width=True)

    # 3. Table
    st.dataframe(df_tickets, use_container_width=True)

    # 4. Action: Create Ticket (Available to ALL users)
    with st.expander("➕ Create Support Ticket"):
        with st.form("ticket_form"):
            t_prio = st.selectbox("Priority", ["Low", "Medium", "High"])
            t_desc = st.text_input("Issue Description")
            t_assign = st.selectbox(
                "Assign To", ["Support Team A", "Network Team", "Admin"])

            if st.form_submit_button("Submit Ticket"):
                insert_ticket(t_prio, t_desc, "Pending",
                              t_assign, str(datetime.now()), 0)
                st.success("Ticket Created")
                st.rerun()

# ==========================================
# DOMAIN 3: DATA SCIENCE
# ==========================================
elif domain == "📊 Data Science":
    df_data = list_datasets()

    # 1. Metrics
    d1, d2 = st.columns(2)
    d1.metric("Available Datasets", len(df_data))
    total_rows = df_data['rows'].sum() if not df_data.empty else 0
    d2.metric("Total Data Points", f"{total_rows:,}")

    # 2. Table
    st.subheader("Metadata Registry")
    st.dataframe(df_data, use_container_width=True)

    # 3. Action: Upload Dataset (Admin Only)
    if st.session_state.role == 'admin':
        st.subheader("📤 Upload New Dataset")
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            if st.button("Process Upload"):
                # Save to disk
                save_path = f"DATA/{uploaded_file.name}"
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Load to DB
                try:
                    # Generic load: table name is filename without extension
                    table_name = uploaded_file.name.split('.')[0]
                    rows_count = load_csv_to_table(
                        save_path, table_name, if_exists='replace')
                    st.success(
                        f"Success! Loaded {rows_count} rows into table '{table_name}'.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading data: {e}")
    else:
        st.info("🔒 Only Admins can upload new datasets.")
