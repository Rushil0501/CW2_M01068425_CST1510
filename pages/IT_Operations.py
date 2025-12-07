# pages/IT_Operations.py
import streamlit as st
from datetime import datetime
from pathlib import Path
import os

from app.ui.styles import load_custom_css
from app.ui.charts import render_chart

from app.data.tickets import get_all_tickets, insert_ticket
from app.data.datasets import load_csv_to_table

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

st.set_page_config(page_title="IT Operations Dashboard", layout="wide")
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
st.session_state.last_page = "pages/IT_Operations.py"

# ---------------- header with avatar ----------------
col_a, col_b, col_c = st.columns([1, 6, 2])

with col_a:
    user = get_user_by_username(username)
    avatar = user.get("avatar") if user else None

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

# ---------------- load tickets ----------------
try:
    df = get_all_tickets()
except Exception as e:
    st.error(f"Failed to load tickets: {e}")
    df = None

main_col, ai_col = st.columns([8, 3])

with main_col:
    st.subheader("📊 IT Analytics Overview")
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        render_chart(df, chart_type="pie", x="status", title="Ticket Status")

    with c2:
        render_chart(df, chart_type="bar", x="priority",
                     color="status", title="Tickets by Priority")

    with c3:
        render_chart(df, chart_type="line", x="created_at",
                     title="Tickets Over Time")

    st.markdown("---")

    st.subheader("📄 IT Tickets (raw)")
    if df is None or df.empty:
        st.info("No tickets.")
    else:
        st.dataframe(df, use_container_width=True, height=360)

    st.markdown("---")
    st.subheader("📤 Upload Tickets CSV (same schema)")
    with st.form("upload_tickets"):
        f = st.file_uploader("Drop CSV or click", type="csv")
        mode = st.selectbox("Upload mode", ["append", "replace"])
        go = st.form_submit_button("Upload")
        if go:
            if not f:
                st.error("Select CSV")
            else:
                p = Path("DATA")
                p.mkdir(exist_ok=True)
                tmp = p / \
                    f"uploaded_it_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                with open(tmp, "wb") as fh:
                    fh.write(f.getbuffer())
                try:
                    load_csv_to_table(
                        str(tmp), "it_tickets", if_exists="replace" if mode == "replace" else "append")
                    st.success("Uploaded.")
                    reload_page()
                except Exception as e:
                    st.error(f"Failed: {e}")

    st.markdown("---")
    st.subheader("➕ Add Ticket (Quick Add)")
    with st.form("add_ticket"):
        pri = st.selectbox("Priority", ["Low", "Medium", "High"])
        descr = st.text_input("Issue")
        assign = st.text_input("Assigned to", value="Admin")
        add = st.form_submit_button("Create")
        if add:
            try:
                insert_ticket(pri, descr, "Pending", assign,
                              datetime.now().isoformat(), 0)
                st.success("Ticket created.")
                reload_page()
            except Exception as e:
                st.error(f"Failed to create ticket: {e}")

with ai_col:
    st.subheader("🧠 IT AI")
    history = load_ai_history(username, "it") or []

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
    q = st.text_input("Ask the IT AI assistant...", key="it_query")
    if st.button("Send IT", key="it_send"):
        if q:
            try:
                save_ai_message(username, "it", "user", q)
            except:
                pass
            chat_history = [{"role": r["role"], "content": r["content"]}
                            for r in history]
            if get_gemini_response:
                placeholder = st.empty()
                full = ""
                try:
                    stream = get_gemini_response(q, chat_history, "it")
                    for chunk in stream:
                        if hasattr(chunk, "text"):
                            full += chunk.text
                            placeholder.markdown(
                                f"<div class='ai-response'>{full}▌</div>", unsafe_allow_html=True)
                    placeholder.markdown(
                        f"<div class='ai-response'>{full}</div>", unsafe_allow_html=True)
                    save_ai_message(username, "it", "assistant", full)
                except Exception as e:
                    st.error(f"AI Error: {e}")
            else:
                fallback = f"[Local] Received: {q}"
                st.markdown(
                    f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
                try:
                    save_ai_message(username, "it", "assistant", fallback)
                except:
                    pass
            reload_page()

    if st.button("🧹 Clear IT Chat History"):
        try:
            delete_ai_history(username, "it")
            st.success("Cleared.")
            reload_page()
        except Exception as e:
            st.error(f"Failed: {e}")
