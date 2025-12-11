import streamlit as st
from datetime import datetime
from pathlib import Path

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

from app.services.user_service import get_user_by_username

st.set_page_config(page_title="IT Operations Dashboard", layout="wide")
load_custom_css()


class ITOperationsDashboard:
    def __init__(self):
        self.qp = st.query_params
        self.username = None
        self.role = None
        self.user = None
        self.df = None

    @staticmethod
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

    def authenticate(self):
        if "user" not in self.qp or not self.qp.get("user"):
            st.query_params.clear()
            st.switch_page("Home.py")
            st.stop()

        self.username = self.qp.get("user")[0]
        self.role = self.qp.get("role", [""])[0]
        st.session_state.last_page = "pages/IT_Operations.py"

    def render_header(self):
        col_a, col_b, col_c = st.columns([1, 6, 2])

        with col_a:
            self.user = get_user_by_username(self.username)
            avatar = self.user.get("avatar") if self.user else None

            if avatar:
                st.image(avatar, width=70)
                st.markdown(
                    "<style>img{border-radius:50%; border:3px solid #FF1493;}</style>", unsafe_allow_html=True)
            else:
                initials = "".join([p[0].upper()
                                   for p in self.username.split()][:2]) or "U"
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
                f"<div style='font-size:20px;font-weight:700;color:white'>{self.username}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='color:#FF1493;font-size:12px;text-transform:uppercase'>{self.role}</div>", unsafe_allow_html=True)

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

    def load_data(self):
        try:
            self.df = get_all_tickets()
        except Exception as e:
            st.error(f"Failed to load tickets: {e}")
            self.df = None

    def render_main_panel(self):
        st.subheader("📊 IT Analytics Overview")
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            render_chart(self.df, chart_type="pie",
                         x="status", title="Ticket Status")

        with c2:
            render_chart(self.df, chart_type="bar", x="priority",
                         color="status", title="Tickets by Priority")

        with c3:
            render_chart(self.df, chart_type="line", x="created_at",
                         title="Tickets Over Time")

        st.markdown("---")

        st.subheader("📄 IT Tickets (raw)")
        if self.df is None or self.df.empty:
            st.info("No tickets.")
        else:
            st.dataframe(self.df, width='stretch', height=360)

        st.markdown("---")
        st.subheader("📤 Upload Tickets CSV (Same schema)")
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
                        st.success("Uploaded successfully.")
                        self.reload_page()
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

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
                    self.reload_page()
                except Exception as e:
                    st.error(f"Failed to create ticket: {e}")

    def render_ai_panel(self):
        st.subheader("🧠 IT AI")
        history = load_ai_history(self.username, "it") or []

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
                    save_ai_message(self.username, "it", "user", q)
                except Exception:
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
                        save_ai_message(self.username, "it", "assistant", full)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
                else:
                    fallback = f"[Local] Received: {q}"
                    st.markdown(
                        f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
                    try:
                        save_ai_message(self.username, "it",
                                        "assistant", fallback)
                    except Exception:
                        pass
                self.reload_page()

        if st.button("🧹 Clear IT Chat History"):
            try:
                delete_ai_history(self.username, "it")
                st.success("Cleared.")
                self.reload_page()
            except Exception as e:
                st.error(f"Failed: {e}")

    def run(self):
        self.authenticate()
        self.render_header()
        self.load_data()
        main_col, ai_col = st.columns([8, 3])

        with main_col:
            self.render_main_panel()

        with ai_col:
            self.render_ai_panel()


if __name__ == "__main__":
    ITOperationsDashboard().run()
