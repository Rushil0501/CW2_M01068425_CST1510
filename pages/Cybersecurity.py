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

from app.services.user_service import get_user_by_username, get_valid_avatar_path

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
            avatar_path = get_valid_avatar_path(self.username, avatar)

            if avatar_path:
                st.image(avatar_path, width=70)
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
        
        # Key Metrics at the top
        if self.df is not None and not self.df.empty:
            total_incidents = len(self.df)
            open_incidents = len(self.df[self.df.get('status', pd.Series()).str.lower() == 'open']) if 'status' in self.df.columns else 0
            closed_incidents = len(self.df[self.df.get('status', pd.Series()).str.lower() == 'closed']) if 'status' in self.df.columns else 0
            critical_incidents = len(self.df[self.df.get('severity', pd.Series()).str.lower() == 'critical']) if 'severity' in self.df.columns else 0
            high_severity = len(self.df[self.df.get('severity', pd.Series()).str.lower() == 'high']) if 'severity' in self.df.columns else 0
            unique_categories = self.df['category'].nunique() if 'category' in self.df.columns else 0
            resolved_rate = round((closed_incidents / total_incidents * 100), 1) if total_incidents > 0 else 0
            
            # First row of metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Total Incidents", total_incidents)
            with metric_col2:
                st.metric("Open Incidents", open_incidents)
            with metric_col3:
                st.metric("Closed Incidents", closed_incidents)
            with metric_col4:
                st.metric("Resolution Rate", f"{resolved_rate}%")
            
            # Second row of metrics
            metric_col5, metric_col6, metric_col7, metric_col8 = st.columns(4)
            with metric_col5:
                st.metric("Critical Severity", critical_incidents)
            with metric_col6:
                st.metric("High Severity", high_severity)
            with metric_col7:
                st.metric("Unique Categories", unique_categories)
            with metric_col8:
                most_common_category = self.df['category'].mode()[0] if 'category' in self.df.columns and not self.df['category'].mode().empty else "N/A"
                st.metric("Most Common Category", most_common_category)
            
            st.markdown("---")
        
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
        
        # Additional Visualizations Section - Direct Display
        st.markdown("### 📈 Advanced Analytics")
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
        else:
            st.info("No data available for advanced analytics")

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
                # Automatically send the question
                history = load_ai_history(self.username, "cyber") or []
                save_ai_message(self.username, "cyber", "user", question)
                chat_history = [{"role": m["role"], "content": m["content"]}
                                for m in history]

                if get_gemini_response:
                    typing_placeholder = st.empty()
                    # Show typing animation
                    typing_placeholder.markdown(
                        "<div class='ai-chat-bubble-assistant'><strong>AI:</strong> <span>Typing<span class='typing-dots'><span>.</span><span>.</span><span>.</span></span></span></div>", 
                        unsafe_allow_html=True
                    )
                    full = ""
                    try:
                        for chunk in get_gemini_response(question, chat_history, "cyber"):
                            if hasattr(chunk, "text"):
                                full += chunk.text
                                typing_placeholder.markdown(
                                    f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {full}▌</div>", 
                                    unsafe_allow_html=True
                                )
                        typing_placeholder.markdown(
                            f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {full}</div>", 
                            unsafe_allow_html=True
                        )
                        save_ai_message(self.username, "cyber", "assistant", full)
                    except Exception as e:
                        error_msg = f"⚠️ AI Error: {str(e)}"
                        typing_placeholder.markdown(
                            f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {error_msg}</div>", 
                            unsafe_allow_html=True
                        )
                        save_ai_message(self.username, "cyber", "assistant", error_msg)
                else:
                    fallback = f"[Local] Received: {question}"
                    save_ai_message(self.username, "cyber", "assistant", fallback)
                
                st.rerun()

        st.markdown("---")

        history = load_ai_history(self.username, "cyber") or []
        
        # Show last message outside, previous history in dropdown
        if history:
            # Find the last user message (question) and its answer
            last_user_msg = None
            last_user_idx = None
            for i in range(len(history) - 1, -1, -1):
                if history[i]["role"] == "user":
                    last_user_msg = history[i]
                    last_user_idx = i
                    break
            
            # Display last message/question directly (not in expander)
            if last_user_msg:
                st.markdown("### 💬 Last Message")
                st.markdown(f"<div class='ai-chat-bubble-user'><strong>You:</strong> {last_user_msg['content']}</div>", unsafe_allow_html=True)
                st.caption(last_user_msg["timestamp"])
                
                # Show the corresponding answer if it exists
                if last_user_idx + 1 < len(history) and history[last_user_idx + 1]["role"] == "assistant":
                    answer = history[last_user_idx + 1]
                    st.markdown(f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {answer['content']}</div>", unsafe_allow_html=True)
                    st.caption(answer["timestamp"])
                
                # Show previous history in dropdown
                if len(history) > 2:  # More than just the last Q&A pair
                    previous_history = history[:last_user_idx]
                    if previous_history:
                        with st.expander("💬 Previous Chat History", expanded=False):
                            for msg in previous_history:
                                cls = "ai-chat-bubble-user" if msg["role"] == "user" else "ai-chat-bubble-assistant"
                                who = "You" if msg["role"] == "user" else "AI"
                                st.markdown(f"<div class='{cls}'><strong>{who}:</strong> {msg['content']}</div>", unsafe_allow_html=True)
                                st.caption(msg["timestamp"])
            else:
                st.info("No questions asked yet. Try asking a question above!")
        else:
            st.info("No chat history. Try asking a question above!")

        st.markdown("---")
        
        # Function to handle sending message - sets flag instead of processing immediately
        def send_message():
            if "cyber_ai_input" in st.session_state and st.session_state.cyber_ai_input:
                st.session_state.cyber_send_trigger = True
        
        # Check if we need to process a message
        if st.session_state.get("cyber_send_trigger", False) and st.session_state.get("cyber_ai_input"):
            user_message = st.session_state.cyber_ai_input
            st.session_state.cyber_send_trigger = False
            
            save_ai_message(self.username, "cyber", "user", user_message)
            chat_history = [{"role": m["role"], "content": m["content"]}
                            for m in history]

            if get_gemini_response:
                full = ""
                typing_placeholder = st.empty()
                # Show typing animation
                typing_placeholder.markdown(
                    "<div class='ai-chat-bubble-assistant'><strong>AI:</strong> <span>Typing<span class='typing-dots'><span>.</span><span>.</span><span>.</span></span></span></div>", 
                    unsafe_allow_html=True
                )
                try:
                    for chunk in get_gemini_response(user_message, chat_history, "cyber"):
                        if hasattr(chunk, "text"):
                            full += chunk.text
                            typing_placeholder.markdown(
                                f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {full}▌</div>", 
                                unsafe_allow_html=True
                            )
                    typing_placeholder.markdown(
                        f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {full}</div>", 
                        unsafe_allow_html=True
                    )
                    save_ai_message(self.username, "cyber", "assistant", full)
                except Exception as e:
                    error_msg = f"⚠️ AI Error: {str(e)}"
                    typing_placeholder.markdown(
                        f"<div class='ai-chat-bubble-assistant'><strong>AI:</strong> {error_msg}</div>", 
                        unsafe_allow_html=True
                    )
                    save_ai_message(self.username, "cyber", "assistant", error_msg)
            else:
                fallback = f"[Local] Received: {user_message}"
                save_ai_message(self.username, "cyber", "assistant", fallback)
            
            # Clear input and rerun
            st.session_state.cyber_ai_input = ""
            st.rerun()
        
        # Input and send
        ai_input = st.text_input(
            "Ask the Cyber AI… (Press Enter to send)", 
            key="cyber_ai_input",
            on_change=send_message
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Send", key="cyber_send"):
                send_message()
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
