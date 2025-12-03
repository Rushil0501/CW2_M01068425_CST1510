import streamlit as st
from datetime import datetime
from app.data.tickets import get_all_tickets, insert_ticket
from pages.AI_Assistant import render_ai_console
from app.ui.styles import set_visuals
set_visuals()


st.set_page_config(page_title="IT Operations", layout="wide")

# Security Guard
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")

if st.session_state.role != "it":
    st.error("Access denied.")
    st.stop()

st.title("🛠️ IT Operations Support")

df = get_all_tickets()

col1, col2 = st.columns(2)
col1.metric("Total Tickets", len(df))
col2.metric("Pending", len(df[df["status"] == "Pending"]))

st.dataframe(df, use_container_width=True)

with st.form("new_ticket"):
    st.subheader("➕ Create New Ticket")
    priority = st.selectbox("Priority", ["Low", "High"])
    issue = st.text_input("Describe the issue")
    if st.form_submit_button("Create Ticket"):
        insert_ticket(priority, issue, "Pending", st.session_state.username,
                      str(datetime.now()), 0)
        st.success("Ticket created.")
        st.rerun()


render_ai_console("it")
