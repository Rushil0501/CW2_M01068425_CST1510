# pages/Cybersecurity.py
import streamlit as st
from datetime import datetime
from pathlib import Path
import os

from app.ui.styles import load_custom_css
from app.ui.charts import render_chart

from app.data.incidents import get_all_incidents, insert_incident
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

st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")
load_custom_css()


class CybersecurityDashboard:
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
        st.session_state.last_page = "pages/Cybersecurity.py"

    def render_header(self):
        col_a, col_b, col_c = st.columns([1, 6, 2])

        with col_a:
            self.user = get_user_by_username(self.username)
            avatar = self.user.get("avatar") if self.user else None

            if avatar and os.path.exists(avatar):
                st.image(avatar, width=70)
                st.markdown(
                    "<style>img{border-radius:50%; border:3px solid #FF1493;}</style>",
                    unsafe_allow_html=True
                )
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
            self.df = get_all_incidents()
        except Exception as e:
            st.error(f"Failed to load incidents: {e}")
            self.df = None

    def render_main_panel(self):
        st.subheader("📊 Cybersecurity Analytics Overview")
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            st.markdown("### 🔥 Severity")
            render_chart(self.df, "pie", "severity", title="Severity Breakdown")

        with c2:
            st.markdown("### 🧩 Category")
            render_chart(self.df, "bar", "category", color="severity",
                         title="Incidents by Category")

        with c3:
            st.markdown("### 📈 Trend")
            render_chart(self.df, "line", "timestamp", title="Incident Trend")

        st.markdown("---")

        st.subheader("📄 Cyber Incidents (raw)")
        if self.df is None or self.df.empty:
            st.info("No incidents available.")
        else:
            st.dataframe(self.df, use_container_width=True, height=360)

        st.markdown("---")

        st.subheader("📤 Upload incidents CSV")
        with st.form("upload_csv"):
            file = st.file_uploader("Upload CSV", type="csv")
            mode = st.selectbox("Mode", ["append", "replace"])
            ok = st.form_submit_button("Upload")
            if ok and file:
                tmp = Path("DATA") / \
                    f"inc_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                tmp.parent.mkdir(exist_ok=True)
                tmp.write_bytes(file.getbuffer())
                load_csv_to_table(str(tmp), "cyber_incidents",
                                  if_exists="replace" if mode == "replace" else "append")
                self.reload_page()

        st.markdown("---")

        st.subheader("➕ Add Incident")
        with st.form("add_incident"):
            sev = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            cat = st.text_input("Category", "Phishing")
            status = st.selectbox("Status", ["Open", "Closed"])
            desc = st.text_area("Description")
            if st.form_submit_button("Add"):
                insert_incident(datetime.now().isoformat(),
                                sev, cat, status, desc)
                self.reload_page()

    def render_ai_panel(self):
        st.subheader("🧠 Cyber AI")

        history = load_ai_history(self.username, "cyber") or []
        for msg in history:
            cls = "ai-chat-bubble-user" if msg["role"] == "user" else "ai-chat-bubble-assistant"
            st.markdown(
                f"<div class='{cls}'>{msg['content']}</div>", unsafe_allow_html=True)
            st.caption(msg["timestamp"])

        ai_input = st.text_input("Ask the Cyber AI…")
        if st.button("Send") and ai_input:
            save_ai_message(self.username, "cyber", "user", ai_input)
            chat_history = [{"role": m["role"], "content": m["content"]}
                            for m in history]

            if get_gemini_response:
                full = ""
                placeholder = st.empty()
                for chunk in get_gemini_response(ai_input, chat_history, "cyber"):
                    if hasattr(chunk, "text"):
                        full += chunk.text
                        placeholder.markdown(full + "▌")
                save_ai_message(self.username, "cyber", "assistant", full)

            self.reload_page()

        if st.button("🧹 Clear Chat History"):
            delete_ai_history(self.username, "cyber")
            self.reload_page()

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
    CybersecurityDashboard().run()
