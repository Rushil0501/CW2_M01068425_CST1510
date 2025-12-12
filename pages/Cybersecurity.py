import streamlit as st
from datetime import datetime
from pathlib import Path
import os
import pandas as pd

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
            render_chart(self.df, "pie", "severity",
                         title="Severity Breakdown")

        with c2:
            st.markdown("### 🧩 Category")
            render_chart(self.df, "bar", "category", color="severity",
                         title="Incidents by Category")

        with c3:
            st.markdown("### 📈 Trend")
            render_chart(self.df, "line", "timestamp", title="Incident Trend")

        st.markdown("---")
        
        # Additional Visualizations Section - Compact View
        with st.expander("📈 Advanced Analytics", expanded=False):
            if self.df is not None and not self.df.empty:
                # Row 1: Status Distribution and Severity vs Status
                r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1, 1, 1, 1])
                
                with r1_col1:
                    st.markdown("#### 📊 Status")
                    render_chart(self.df, "pie", "status", title="Status")
                
                with r1_col2:
                    st.markdown("#### 🔍 Severity")
                    render_chart(self.df, "box", x="status", y="severity", 
                               title="Severity by Status")
                
                with r1_col3:
                    st.markdown("#### 🔥 Heatmap")
                    if "severity" in self.df.columns and "category" in self.df.columns:
                        render_chart(self.df, "heatmap", groupby=["severity", "category"],
                                   title="Severity-Category")
                
                with r1_col4:
                    st.markdown("#### 📊 Category")
                    render_chart(self.df, "histogram", x="category", 
                               title="Category Dist")
                
                # Row 2: Time-based analysis
                if "timestamp" in self.df.columns:
                    try:
                        df_time = self.df.copy()
                        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
                        df_time = df_time.dropna(subset=['timestamp'])
                        
                        if not df_time.empty:
                            df_time['date'] = df_time['timestamp'].dt.date
                            df_time['hour'] = df_time['timestamp'].dt.hour
                            df_time['day_of_week'] = df_time['timestamp'].dt.day_name()
                            
                            time_col1, time_col2 = st.columns([1, 1])
                            
                            with time_col1:
                                day_counts = df_time['day_of_week'].value_counts()
                                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                                day_counts = day_counts.reindex([d for d in day_order if d in day_counts.index], fill_value=0)
                                day_df = pd.DataFrame({'day': day_counts.index, 'count': day_counts.values})
                                render_chart(day_df, "bar", x="day", y="count",
                                           title="By Day")
                            
                            with time_col2:
                                hour_counts = df_time['hour'].value_counts().sort_index()
                                hour_df = pd.DataFrame({'hour': hour_counts.index, 'count': hour_counts.values})
                                render_chart(hour_df, "line", x="hour", y="count",
                                           title="By Hour")
                    except Exception:
                        pass
                
                # Row 3: Status trends
                if "timestamp" in self.df.columns and "status" in self.df.columns:
                    try:
                        df_status_time = self.df.copy()
                        df_status_time['timestamp'] = pd.to_datetime(df_status_time['timestamp'], errors='coerce')
                        df_status_time = df_status_time.dropna(subset=['timestamp'])
                        df_status_time['date'] = df_status_time['timestamp'].dt.date
                        
                        status_counts = df_status_time.groupby(['date', 'status']).size().reset_index(name='count')
                        render_chart(status_counts, "area", x="date", y="count", color="status",
                                   title="Status Trends")
                    except Exception:
                        pass

        st.markdown("---")

        st.subheader("📄 Cyber Incidents Data & AI Assistant")
        data_col, ai_col = st.columns([2, 1])
        
        with data_col:
            if self.df is None or self.df.empty:
                st.info("No incidents available.")
            else:
                st.dataframe(self.df, height=500)
        
        with ai_col:
            self.render_ai_panel()

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
                try:
                    load_csv_to_table(str(tmp), "cyber_incidents",
                                      if_exists="replace" if mode == "replace" else "append")
                    st.success("Uploaded successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

        st.markdown("---")

        st.subheader("➕ Add Incident")
        with st.form("add_incident"):
            sev = st.selectbox(
                "Severity", ["Low", "Medium", "High", "Critical"])
            cat = st.text_input("Category", "Phishing")
            status = st.selectbox("Status", ["Open", "Closed"])
            desc = st.text_area("Description")
            if st.form_submit_button("Add"):
                # Validate required fields
                if not cat or not cat.strip():
                    st.error("Category is required.")
                elif not desc or not desc.strip():
                    st.error("Description is required.")
                else:
                    try:
                        insert_incident(datetime.now().isoformat(),
                                        sev, cat.strip(), status, desc.strip())
                        st.success("Incident added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add incident: {e}")

    def render_ai_panel(self):
        st.markdown("### 🧠 Cyber AI Assistant")
        
        # Example questions
        example_questions = [
            "What are the most common types of security incidents?",
            "Which severity level has the most incidents?",
            "Show me trends in cybersecurity threats",
            "What percentage of incidents are still open?",
            "Analyse the incident patterns by category",
            "What are the critical security incidents?"
        ]
        
        st.markdown("<div style='margin-bottom: 10px;'><strong style='color: #FF1493;'>💡 Example Questions:</strong></div>", unsafe_allow_html=True)
        
        # Display example questions as buttons
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_cyber_{i}"):
                # Set the question in session state to populate input
                st.session_state["cyber_ai_input"] = question
                st.rerun()

        st.markdown("---")

        history = load_ai_history(self.username, "cyber") or []
        
        # Chat history container with scroll
        chat_container = st.container()
        with chat_container:
            if history:
                for msg in history:
                    cls = "ai-chat-bubble-user" if msg["role"] == "user" else "ai-chat-bubble-assistant"
                    st.markdown(
                        f"<div class='{cls}'>{msg['content']}</div>", unsafe_allow_html=True)
                    st.caption(msg["timestamp"])
            else:
                st.info("No chat history. Try asking a question above!")

        st.markdown("---")
        
        # Input and send
        ai_input = st.text_input("Ask the Cyber AI…", key="cyber_ai_input")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Send", key="cyber_send") and ai_input:
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

                st.rerun()
        
        with col2:
            if st.button("🧹 Clear", key="cyber_clear"):
                delete_ai_history(self.username, "cyber")
                st.rerun()

    def run(self):
        self.authenticate()
        self.render_header()
        self.load_data()
        self.render_main_panel()


if __name__ == "__main__":
    CybersecurityDashboard().run()
