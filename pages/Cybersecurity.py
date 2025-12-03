import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.incidents import get_all_incidents, insert_incident
from app.services.ai_service import get_gemini_response
from pages.AI_Assistant import render_ai_console
from app.ui.styles import set_visuals
set_visuals()


st.set_page_config(page_title="Cybersecurity Ops", layout="wide")

# Security Guard
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")

if st.session_state.role not in ["cyber", "admin"]:
    st.error("Access denied.")
    st.stop()

st.title("🕵️‍♂️ Cybersecurity Operations")

df = get_all_incidents()

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(df))
col2.metric("Critical", len(df[df["severity"] == "Critical"]))
col3.metric("Open", len(df[df["status"] == "Open"]))

st.dataframe(df, use_container_width=True)

# Submit Incident
with st.form("cyber_report"):
    st.subheader("🚨 Submit New Incident")
    cat = st.selectbox("Type", ["Phishing", "Malware", "DDoS"])
    sev = st.selectbox("Severity", ["High", "Critical"])
    desc = st.text_area("Description")
    if st.form_submit_button("Submit"):
        insert_incident(str(datetime.now()), sev, cat, "Open", desc)
        st.success("Incident submitted.")
        st.rerun()


render_ai_console("cyber")
