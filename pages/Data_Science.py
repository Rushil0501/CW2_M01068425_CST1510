import streamlit as st
from app.data.datasets import list_datasets, load_csv_to_table
from pages.AI_Assistant import render_ai_console
from app.ui.styles import set_visuals
set_visuals()


st.set_page_config(page_title="Data Science Lab", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")

if st.session_state.role != "data":
    st.error("Access denied.")
    st.stop()

st.title("🧠 Data Science Lab")

df = list_datasets()
st.metric("Total Datasets", len(df))
st.dataframe(df, use_container_width=True)

st.subheader("📤 Upload New Dataset")
uploaded = st.file_uploader("Upload CSV", type="csv")

if uploaded:
    path = f"DATA/{uploaded.name}"
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())

    load_csv_to_table(path, uploaded.name.split(".")[0], "replace")
    st.success("Dataset uploaded.")
    st.rerun()


render_ai_console("data")
