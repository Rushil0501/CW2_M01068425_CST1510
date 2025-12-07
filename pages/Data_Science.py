# pages/Data_Science.py
import streamlit as st
from datetime import datetime
from pathlib import Path
import os
import pandas as pd

from app.ui.styles import load_custom_css
from app.ui.charts import render_chart

from app.data.datasets import list_datasets, load_csv_to_table
from DATA.ai_history import (
    load_history as load_ai_history,
    save_message as save_ai_message,
    delete_history as delete_ai_history
)

try:
    from app.services.ai_service import get_gemini_response
except Exception:
    get_gemini_response = None

from app.data.db import connect_database
from app.services.user_service import get_user_by_username

st.set_page_config(page_title="Data Science Dashboard", layout="wide")
load_custom_css()

# ---------------- reload helper ----------------


def reload_page():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
            return
    except Exception:
        pass
    st.markdown("<script>window.location.reload();</script>",
                unsafe_allow_html=True)
    st.stop()


# ---------------- auth ----------------
qp = st.query_params
if "user" not in qp or not qp.get("user"):
    st.query_params.clear()
    st.switch_page("Home.py")
    st.stop()

username = qp.get("user")[0]
role = qp.get("role", [""])[0]

# set last_page for profile back
st.session_state.last_page = "pages/Data_Science.py"

# ---------------- header with avatar ----------------
col_a, col_b, col_c = st.columns([1, 6, 2])

with col_a:
    user = get_user_by_username(username)
    avatar = user.get("avatar") if user else None

    # Render avatar image directly (st.image) to avoid local-path html issues
    if avatar:
        st.image(avatar, width=70)
        st.markdown(
            "<style>img{border-radius:50%; border:3px solid #FF1493;}</style>", unsafe_allow_html=True)
    else:
        initials = "".join([p[0].upper() for p in username.split()][:2]) or "U"
        st.markdown(
            f"""
            <div style="width:70px;height:70px;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;
                        background:#111;border:3px solid #FF1493;
                        color:white;font-size:26px;font-weight:700;">
                {initials}
            </div>
            """,
            unsafe_allow_html=True
        )

with col_b:
    st.markdown(
        f"<div style='font-size:20px;font-weight:700;color:white'>{username}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:#FF1493;font-size:12px;text-transform:uppercase'>{role}</div>", unsafe_allow_html=True)

with col_c:
    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("Profile"):
            st.switch_page("pages/profile.py")
    with b2:
        if st.button("Logout"):
            st.query_params.clear()
            st.switch_page("Home.py")

st.markdown("---")

# ---------------- load dataset metadata ----------------
try:
    df = list_datasets()
except Exception as e:
    st.error(f"Failed to load datasets: {e}")
    df = None

main_col, ai_col = st.columns([8, 3])

with main_col:
    st.subheader("📈 Dataset Analytics Overview")
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        st.markdown("### 📊 Columns Distribution")
        if df is not None and "columns" in df.columns:
            render_chart(df, chart_type="pie", x="columns",
                         title="Column Distribution")
        else:
            st.info("No 'columns' field available for pie chart")

    with c2:
        st.markdown("### 📊 Rows per Dataset")
        if df is not None and "rows" in df.columns:
            render_chart(df, chart_type="bar", x="name",
                         y="rows", title="Rows per Dataset")
        else:
            st.info("No 'rows' field available for bar chart")

    with c3:
        st.markdown("### 📈 Upload Trend")
        if df is not None and "upload_date" in df.columns:
            render_chart(df, chart_type="line",
                         x="upload_date", title="Upload Trend")
        else:
            st.info("No 'upload_date' field available")

    st.markdown("---")

    st.subheader("📄 Available Datasets")
    if df is None or df.empty:
        st.info("No datasets found.")
    else:
        st.dataframe(df, use_container_width=True, height=360)

    st.markdown("---")

    st.subheader("📤 Upload Dataset CSV (same schema)")
    with st.form("upload_dataset"):
        f = st.file_uploader("Drop dataset CSV here", type="csv")
        mode = st.selectbox("Upload mode", ["append", "replace"])
        ok = st.form_submit_button("Upload")
        if ok:
            if not f:
                st.error("Choose CSV")
            else:
                dest = Path("DATA")
                dest.mkdir(exist_ok=True)
                tmp = dest / \
                    f"uploaded_dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                with open(tmp, "wb") as fh:
                    fh.write(f.getbuffer())
                try:
                    load_csv_to_table(str(
                        tmp), "datasets_metadata", if_exists="replace" if mode == "replace" else "append")
                    st.success("Uploaded.")
                    reload_page()
                except Exception as e:
                    st.error(f"Failed to import: {e}")

    st.markdown("---")

    st.subheader("➕ Add Dataset (Quick Add)")
    with st.form("add_dataset"):
        nm = st.text_input("Dataset name")
        rows = st.number_input("Rows", min_value=0, step=1)
        cols = st.number_input("Columns", min_value=0, step=1)
        uploaded_by = st.text_input("Uploaded by", value=username)
        upload_date = st.date_input("Upload date")
        add = st.form_submit_button("Add")
        if add:
            try:
                # create a tiny csv row and append
                tmpdir = Path("DATA")
                tmpdir.mkdir(exist_ok=True)
                tmpfile = tmpdir / \
                    f"tmp_new_dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                pd.DataFrame([{
                    "name": nm,
                    "rows": int(rows),
                    "columns": int(cols),
                    "uploaded_by": uploaded_by,
                    "upload_date": upload_date.isoformat()
                }]).to_csv(tmpfile, index=False)
                load_csv_to_table(
                    str(tmpfile), "datasets_metadata", if_exists="append")
                st.success("Dataset added.")
                reload_page()
            except Exception as e:
                st.error(f"Failed to add dataset: {e}")

with ai_col:
    st.subheader("🧠 Data AI")

    history = load_ai_history(username, "data") or []
    if not history:
        st.info("No chat history yet.")
    else:
        for msg in history:
            who = "You" if msg["role"] == "user" else "AI"
            cls = "ai-chat-bubble-user" if msg["role"] == "user" else "ai-chat-bubble-assistant"
            st.markdown(
                f"<div class='{cls}'><strong>{who}:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            st.caption(msg["timestamp"])

    st.markdown("---")
    q = st.text_input("Ask the Data AI assistant...", key="data_query")
    if st.button("Send Data", key="data_send"):
        if q:
            try:
                save_ai_message(username, "data", "user", q)
            except Exception:
                pass
            chat_history = [{"role": r["role"], "content": r["content"]}
                            for r in history]
            if get_gemini_response:
                placeholder = st.empty()
                full = ""
                try:
                    stream = get_gemini_response(q, chat_history, "data")
                    for chunk in stream:
                        if hasattr(chunk, "text"):
                            full += chunk.text
                            placeholder.markdown(
                                f"<div class='ai-response'>{full}▌</div>", unsafe_allow_html=True)
                    placeholder.markdown(
                        f"<div class='ai-response'>{full}</div>", unsafe_allow_html=True)
                    save_ai_message(username, "data", "assistant", full)
                except Exception as e:
                    st.error(f"AI error: {e}")
            else:
                fallback = f"[Local] Received: {q}"
                st.markdown(
                    f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
                try:
                    save_ai_message(username, "data", "assistant", fallback)
                except Exception:
                    pass
            reload_page()

    if st.button("🧹 Clear Data Chat History"):
        try:
            delete_history = delete_ai_history(username, "data")
            st.success("Cleared.")
            reload_page()
        except Exception as e:
            st.error(f"Failed: {e}")
