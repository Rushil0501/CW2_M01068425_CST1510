import streamlit as st
from app.ui.styles import load_custom_css
from DATA.ai_history import load_history as load_ai_history, save_message as save_ai_message, delete_history as delete_ai_history

try:
    from app.services.ai_service import get_gemini_response
except Exception:
    get_gemini_response = None


class AIAssistantPage:
    def __init__(self):
        load_custom_css()
        self.qp = st.query_params
        self.username = None
        self.role = None
        self.user_data = None

    @staticmethod
    def reload_page():
        """Reload page by logging out and redirecting to login."""
        st.query_params.clear()
        if "token" in st.session_state:
            del st.session_state["token"]
        if "user" in st.session_state:
            del st.session_state["user"]
        if "role" in st.session_state:
            del st.session_state["role"]
        st.switch_page("Home.py")
        st.stop()

    def authenticate(self):
        if "user" not in self.qp or not self.qp.get("user"):
            st.query_params.clear()
            st.switch_page("Home.py")
            st.stop()

        self.username = self.qp.get("user")[0]
        self.role = self.qp.get("role", [""])[0]
        st.session_state.last_page = "pages/AI_Assistant.py"

    def render_header(self):
        col_a, col_b, col_c = st.columns([1, 6, 2])

        with col_a:
            from app.services.user_service import get_user_by_username, get_valid_avatar_path
            self.user_data = get_user_by_username(self.username)
            avatar = self.user_data.get("avatar") if self.user_data else None
            avatar_path = get_valid_avatar_path(self.username, avatar)

            if avatar_path:
                st.image(avatar_path, width=70)
                st.markdown(
                    """
                    <style>
                    img {
                        border-radius: 50%;
                        border: 3px solid #FF1493;
                        box-shadow: 0 0 10px rgba(255,20,147,0.6);
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
            else:
                initials = "".join([p[0].upper()
                                   for p in self.username.split()][:2]) or "U"
                st.markdown(
                    f"""
                    <div style="width:70px; height:70px; border-radius:50%;
                                display:flex; align-items:center; justify-content:center;
                                background:#111; border:3px solid #FF1493;
                                color:white; font-weight:700; font-size:26px;
                                box-shadow:0 0 10px rgba(255,20,147,0.6);">
                        {initials}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_b:
            st.markdown(
                f"<div style='font-size:20px; font-weight:700; color:white'>{self.username}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='color:#FF1493; font-size:12px; text-transform:uppercase'>{self.role}</div>",
                unsafe_allow_html=True
            )

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

    def render_chat(self):
        st.subheader("🧠 Enterprise AI Assistant (general)")
        history = load_ai_history(self.username, self.role or "general") or []
        if history:
            for msg in history:
                who = "You" if msg["role"] == "user" else "AI"
                cls = "ai-chat-bubble-user" if msg["role"] == "user" else "ai-chat-bubble-assistant"
                st.markdown(
                    f"<div class='{cls}'><strong>{who}:</strong> {msg['content']}</div>", unsafe_allow_html=True)
                st.caption(msg["timestamp"])
        else:
            st.info("No chat history yet.")

        q = st.text_input("Ask the AI assistant...", key="ai_query")
        if st.button("Send AI", key="ai_send"):
            self.handle_send(q, history)

    def handle_send(self, q, history):
        if not q:
            return

        save_ai_message(self.username, self.role or "general", "user", q)
        chat_history = [{"role": r["role"], "content": r["content"]}
                        for r in history]
        if get_gemini_response:
            placeholder = st.empty()
            full = ""
            try:
                stream = get_gemini_response(
                    q, chat_history, self.role or "general")
                for chunk in stream:
                    if hasattr(chunk, "text"):
                        full += chunk.text
                        placeholder.markdown(
                            f"<div class='ai-response'>{full}▌</div>", unsafe_allow_html=True)
                placeholder.markdown(
                    f"<div class='ai-response'>{full}</div>", unsafe_allow_html=True)
                save_ai_message(self.username, self.role or "general",
                                "assistant", full)
            except Exception as e:
                st.error(f"AI error: {e}")
        else:
            fallback = f"[Local] Received: {q}"
            st.markdown(
                f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
            save_ai_message(self.username, self.role or "general",
                            "assistant", fallback)

        st.rerun()

    def run(self):
        self.authenticate()
        self.render_header()
        self.render_chat()


if __name__ == "__main__":
    AIAssistantPage().run()
