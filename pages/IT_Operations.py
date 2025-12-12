import streamlit as st
from datetime import datetime
from pathlib import Path
import pandas as pd

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

from app.services.user_service import get_user_by_username, get_valid_avatar_path

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
        st.session_state.last_page = "pages/IT_Operations.py"

    def render_header(self):
        col_a, col_b, col_c = st.columns([1, 6, 2])

        with col_a:
            self.user = get_user_by_username(self.username)
            avatar = self.user.get("avatar") if self.user else None
            avatar_path = get_valid_avatar_path(self.username, avatar)

            if avatar_path:
                st.image(avatar_path, width=70)
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
        
        # Key Metrics at the top
        if self.df is not None and not self.df.empty:
            total_tickets = len(self.df)
            open_tickets = len(self.df[self.df.get('status', pd.Series()).str.lower() == 'open']) if 'status' in self.df.columns else 0
            resolved_tickets = len(self.df[self.df.get('status', pd.Series()).str.lower().isin(['resolved', 'closed'])]) if 'status' in self.df.columns else 0
            high_priority = len(self.df[self.df.get('priority', pd.Series()).str.lower().isin(['high', 'critical'])]) if 'priority' in self.df.columns else 0
            unique_assignees = self.df['assigned_to'].nunique() if 'assigned_to' in self.df.columns else 0
            avg_resolution_hours = round(self.df['resolution_time_hours'].mean(), 1) if 'resolution_time_hours' in self.df.columns else 0
            resolution_rate = round((resolved_tickets / total_tickets * 100), 1) if total_tickets > 0 else 0
            
            # First row of metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Total Tickets", total_tickets)
            with metric_col2:
                st.metric("Open Tickets", open_tickets)
            with metric_col3:
                st.metric("Resolved Tickets", resolved_tickets)
            with metric_col4:
                st.metric("Resolution Rate", f"{resolution_rate}%")
            
            # Second row of metrics
            metric_col5, metric_col6, metric_col7, metric_col8 = st.columns(4)
            with metric_col5:
                st.metric("High Priority", high_priority)
            with metric_col6:
                st.metric("Active Assignees", unique_assignees)
            with metric_col7:
                st.metric("Avg Resolution Time", f"{avg_resolution_hours}h")
            with metric_col8:
                most_common_priority = self.df['priority'].mode()[0] if 'priority' in self.df.columns and not self.df['priority'].mode().empty else "N/A"
                st.metric("Most Common Priority", most_common_priority)
            
            st.markdown("---")
        
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
        
        # Additional Visualizations Section
        # Advanced Analytics - Direct Display
        st.markdown("### 📈 Advanced IT Analytics")
        if self.df is not None and not self.df.empty:
                # Row 1: Multiple small charts
                r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1, 1, 1, 1])
                
                with r1_col1:
                    st.markdown("#### 👥 Assignee")
                    if "assigned_to" in self.df.columns:
                        render_chart(self.df, "bar", x="assigned_to", 
                                   title="By Assignee")
                
                with r1_col2:
                    st.markdown("#### 📊 Priority")
                    render_chart(self.df, "histogram", x="priority",
                               title="Priority Dist")
                
                with r1_col3:
                    st.markdown("#### 🔥 Heatmap")
                    if "priority" in self.df.columns and "status" in self.df.columns:
                        render_chart(self.df, "heatmap", groupby=["priority", "status"],
                                   title="Priority-Status")
                
                with r1_col4:
                    st.markdown("#### ⏱️ Resolution")
                    if "resolution_time_hours" in self.df.columns:
                        render_chart(self.df, "box", x="priority", 
                                   y="resolution_time_hours",
                                   title="Res Time")
                
                # Row 2: Time-based
                if "created_at" in self.df.columns:
                    try:
                        df_time = self.df.copy()
                        df_time['created_at'] = pd.to_datetime(df_time['created_at'], errors='coerce')
                        df_time = df_time.dropna(subset=['created_at'])
                        
                        if not df_time.empty:
                            df_time['day_of_week'] = df_time['created_at'].dt.day_name()
                            df_time['hour'] = df_time['created_at'].dt.hour
                            
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
                if "created_at" in self.df.columns and "status" in self.df.columns:
                    try:
                        df_status_time = self.df.copy()
                        df_status_time['created_at'] = pd.to_datetime(df_status_time['created_at'], errors='coerce')
                        df_status_time = df_status_time.dropna(subset=['created_at'])
                        df_status_time['date'] = df_status_time['created_at'].dt.date
                        
                        status_counts = df_status_time.groupby(['date', 'status']).size().reset_index(name='count')
                        render_chart(status_counts, "area", x="date", y="count", color="status",
                                   title="Status Trends")
                    except Exception:
                        pass
                
                # Row 4: Assignee Performance
                if "assigned_to" in self.df.columns:
                    assignee_col1, assignee_col2 = st.columns([1, 1])
                    
                    with assignee_col1:
                        if "status" in self.df.columns:
                            assignee_status = self.df.groupby(['assigned_to', 'status']).size().reset_index(name='count')
                            render_chart(assignee_status, "bar", x="assigned_to", y="count", color="status",
                                       title="By Assignee & Status")
                    
                    with assignee_col2:
                        if "resolution_time_hours" in self.df.columns:
                            avg_res = self.df.groupby('assigned_to')['resolution_time_hours'].mean().reset_index()
                            avg_res.columns = ['assigned_to', 'avg_resolution_hours']
                            render_chart(avg_res, "bar", x="assigned_to", y="avg_resolution_hours",
                                       title="Avg Res Time")
        else:
            st.info("No data available for advanced analytics")

        st.markdown("---")

        st.subheader("📄 IT Tickets Data & AI Assistant")
        data_col, ai_col = st.columns([2, 1])
        
        with data_col:
            if self.df is None or self.df.empty:
                st.info("No tickets.")
            else:
                st.dataframe(self.df, height=500)
        
        with ai_col:
            self.render_ai_panel()

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
                        st.rerun()
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
                # Validate required fields
                if not descr or not descr.strip():
                    st.error("Issue description is required.")
                elif not assign or not assign.strip():
                    st.error("Assigned to is required.")
                else:
                    try:
                        insert_ticket(pri, descr.strip(), "Pending", assign.strip(),
                                      datetime.now().isoformat(), 0)
                        st.success("Ticket created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create ticket: {e}")

    def render_ai_panel(self):
        st.markdown("### 🧠 IT AI Assistant")
        
        # Example questions
        example_questions = [
            "What is the average resolution time for tickets?",
            "Which team member has the most assigned tickets?",
            "What are the most common ticket priorities?",
            "Show me ticket trends over time",
            "Which tickets are taking longest to resolve?",
            "What percentage of tickets are still pending?"
        ]
        
        st.markdown("<div style='margin-bottom: 10px;'><strong style='color: #FF1493;'>💡 Example Questions:</strong></div>", unsafe_allow_html=True)
        
        # Display example questions as buttons
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_it_{i}"):
                # Automatically send the question
                history = load_ai_history(self.username, "it") or []
                save_ai_message(self.username, "it", "user", question)
                chat_history = [{"role": r["role"], "content": r["content"]}
                                for r in history]

                if get_gemini_response:
                    typing_placeholder = st.empty()
                    # Show typing animation
                    typing_placeholder.markdown(
                        "<div class='ai-response'><strong>AI:</strong> <span>Typing<span class='typing-dots'><span>.</span><span>.</span><span>.</span></span></span></div>", 
                        unsafe_allow_html=True
                    )
                    full = ""
                    try:
                        for chunk in get_gemini_response(question, chat_history, "it"):
                            if hasattr(chunk, "text"):
                                full += chunk.text
                                typing_placeholder.markdown(
                                    f"<div class='ai-response'><strong>AI:</strong> {full}▌</div>", 
                                    unsafe_allow_html=True
                                )
                        typing_placeholder.markdown(
                            f"<div class='ai-response'><strong>AI:</strong> {full}</div>", 
                            unsafe_allow_html=True
                        )
                        save_ai_message(self.username, "it", "assistant", full)
                    except Exception as e:
                        error_msg = f"⚠️ AI Error: {str(e)}"
                        typing_placeholder.markdown(
                            f"<div class='ai-response'><strong>AI:</strong> {error_msg}</div>", 
                            unsafe_allow_html=True
                        )
                        save_ai_message(self.username, "it", "assistant", error_msg)
                else:
                    fallback = f"[Local] Received: {question}"
                    save_ai_message(self.username, "it", "assistant", fallback)
                
                st.rerun()

        st.markdown("---")

        history = load_ai_history(self.username, "it") or []
        
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
            if "it_query" in st.session_state and st.session_state.it_query:
                st.session_state.it_send_trigger = True
        
        # Check if we need to process a message
        if st.session_state.get("it_send_trigger", False) and st.session_state.get("it_query"):
            user_message = st.session_state.it_query
            st.session_state.it_send_trigger = False
            
            try:
                save_ai_message(self.username, "it", "user", user_message)
            except Exception:
                pass
            chat_history = [{"role": r["role"], "content": r["content"]}
                            for r in history]
            
            if get_gemini_response:
                typing_placeholder = st.empty()
                # Show typing animation
                typing_placeholder.markdown(
                    "<div class='ai-response'><strong>AI:</strong> <span>Typing<span class='typing-dots'><span>.</span><span>.</span><span>.</span></span></span></div>", 
                    unsafe_allow_html=True
                )
                full = ""
                try:
                    for chunk in get_gemini_response(user_message, chat_history, "it"):
                        if hasattr(chunk, "text"):
                            full += chunk.text
                            typing_placeholder.markdown(
                                f"<div class='ai-response'><strong>AI:</strong> {full}▌</div>", 
                                unsafe_allow_html=True
                            )
                    typing_placeholder.markdown(
                        f"<div class='ai-response'><strong>AI:</strong> {full}</div>", 
                        unsafe_allow_html=True
                    )
                    save_ai_message(self.username, "it", "assistant", full)
                except Exception as e:
                    error_msg = f"⚠️ AI Error: {str(e)}"
                    typing_placeholder.markdown(
                        f"<div class='ai-response'><strong>AI:</strong> {error_msg}</div>", 
                        unsafe_allow_html=True
                    )
                    save_ai_message(self.username, "it", "assistant", error_msg)
            else:
                fallback = f"[Local] Received: {user_message}"
                st.markdown(
                    f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
                try:
                    save_ai_message(self.username, "it", "assistant", fallback)
                except Exception:
                    pass
            
            # Clear input and rerun
            st.session_state.it_query = ""
            st.rerun()
        
        # Input and send
        q = st.text_input(
            "Ask the IT AI assistant... (Press Enter to send)", 
            key="it_query",
            on_change=send_message
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Send", key="it_send"):
                send_message()
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear", key="it_clear"):
                try:
                    delete_ai_history(self.username, "it")
                    st.success("Cleared.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

    def run(self):
        self.authenticate()
        self.render_header()
        self.load_data()
        self.render_main_panel()


if __name__ == "__main__":
    ITOperationsDashboard().run()
