import streamlit as st
from datetime import datetime
from pathlib import Path
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

from app.services.user_service import get_user_by_username, get_valid_avatar_path

st.set_page_config(page_title="Data Science Dashboard", layout="wide")
load_custom_css()


class DataScienceDashboard:
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
        st.session_state.last_page = "pages/Data_Science.py"

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
            self.df = list_datasets()
        except Exception as e:
            st.error(f"Failed to load datasets: {e}")
            self.df = None

    def render_main_panel(self):
        st.subheader("📈 Dataset Analytics Overview")
        
        # Key Metrics at the top
        if self.df is not None and not self.df.empty:
            total_datasets = len(self.df)
            total_rows = self.df['rows'].sum() if 'rows' in self.df.columns else 0
            total_columns = self.df['columns'].sum() if 'columns' in self.df.columns else 0
            unique_uploaders = self.df['uploaded_by'].nunique() if 'uploaded_by' in self.df.columns else 0
            avg_rows = round(self.df['rows'].mean(), 0) if 'rows' in self.df.columns else 0
            avg_columns = round(self.df['columns'].mean(), 1) if 'columns' in self.df.columns else 0
            total_data_points = total_rows * total_columns if total_rows > 0 and total_columns > 0 else 0
            largest_dataset_rows = int(self.df['rows'].max()) if 'rows' in self.df.columns else 0
            
            # First row of metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Total Datasets", total_datasets)
            with metric_col2:
                st.metric("Total Rows", f"{total_rows:,}")
            with metric_col3:
                st.metric("Total Columns", total_columns)
            with metric_col4:
                st.metric("Total Data Points", f"{total_data_points:,}")
            
            # Second row of metrics
            metric_col5, metric_col6, metric_col7, metric_col8 = st.columns(4)
            with metric_col5:
                st.metric("Unique Uploaders", unique_uploaders)
            with metric_col6:
                st.metric("Avg Rows per Dataset", f"{avg_rows:,.0f}")
            with metric_col7:
                st.metric("Avg Columns per Dataset", f"{avg_columns:.1f}")
            with metric_col8:
                st.metric("Largest Dataset", f"{largest_dataset_rows:,} rows")
            
            st.markdown("---")
        
        c1, c2, c3 = st.columns([1, 1, 1])

        with c1:
            st.markdown("### 📊 Columns Distribution")
            if self.df is not None and "columns" in self.df.columns:
                render_chart(self.df, chart_type="pie", x="columns",
                             title="Column Distribution")
            else:
                st.info("No 'columns' field available for pie chart")

        with c2:
            st.markdown("### 📊 Rows per Dataset")
            if self.df is not None and "rows" in self.df.columns:
                render_chart(self.df, chart_type="bar", x="name",
                             y="rows", title="Rows per Dataset")
            else:
                st.info("No 'rows' field available for bar chart")

        with c3:
            st.markdown("### 📈 Upload Trend")
            if self.df is not None and "upload_date" in self.df.columns:
                render_chart(self.df, chart_type="line",
                             x="upload_date", title="Upload Trend")
            else:
                st.info("No 'upload_date' field available")

        st.markdown("---")
        
        # Additional Visualizations Section
        # Advanced Analytics - Direct Display
        st.markdown("### 📊 Advanced Dataset Analytics")
        if self.df is not None and not self.df.empty:
                # Row 1: Multiple small charts
                r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1, 1, 1, 1])
                
                with r1_col1:
                    st.markdown("#### 📏 Size")
                    if "rows" in self.df.columns and "columns" in self.df.columns:
                        render_chart(self.df, "scatter", x="columns", y="rows",
                                   title="Rows vs Cols")
                
                with r1_col2:
                    st.markdown("#### 👥 Uploader")
                    if "uploaded_by" in self.df.columns:
                        render_chart(self.df, "bar", x="uploaded_by",
                                   title="By Uploader")
                
                with r1_col3:
                    st.markdown("#### 📊 Rows Dist")
                    if "rows" in self.df.columns:
                        render_chart(self.df, "histogram", x="rows",
                                   title="Rows Dist")
                
                with r1_col4:
                    st.markdown("#### 📦 Stats")
                    if "rows" in self.df.columns:
                        render_chart(self.df, "box", y="rows",
                                   title="Rows Box")
                
                # Row 2: Time-based
                if "upload_date" in self.df.columns:
                    try:
                        df_time = self.df.copy()
                        df_time['upload_date'] = pd.to_datetime(df_time['upload_date'], errors='coerce')
                        df_time = df_time.dropna(subset=['upload_date'])
                        
                        if not df_time.empty:
                            df_time['day_of_week'] = df_time['upload_date'].dt.day_name()
                            df_time['month'] = df_time['upload_date'].dt.to_period('M').astype(str)
                            
                            time_col1, time_col2 = st.columns([1, 1])
                            
                            with time_col1:
                                month_counts = df_time['month'].value_counts().sort_index()
                                month_df = pd.DataFrame({'month': month_counts.index, 'count': month_counts.values})
                                render_chart(month_df, "bar", x="month", y="count",
                                           title="By Month")
                            
                            with time_col2:
                                day_counts = df_time['day_of_week'].value_counts()
                                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                                day_counts = day_counts.reindex([d for d in day_order if d in day_counts.index], fill_value=0)
                                day_df = pd.DataFrame({'day': day_counts.index, 'count': day_counts.values})
                                render_chart(day_df, "bar", x="day", y="count",
                                           title="By Day")
                    except Exception:
                        pass
                
                # Row 3: Uploader performance
                if "uploaded_by" in self.df.columns and "rows" in self.df.columns:
                    uploader_col1, uploader_col2 = st.columns([1, 1])
                    
                    with uploader_col1:
                        uploader_rows = self.df.groupby('uploaded_by')['rows'].sum().reset_index()
                        uploader_rows.columns = ['uploaded_by', 'total_rows']
                        render_chart(uploader_rows, "bar", x="uploaded_by", y="total_rows",
                                   title="Total Rows")
                    
                    with uploader_col2:
                        if "columns" in self.df.columns:
                            df_heatmap = self.df.copy()
                            df_heatmap['size_category'] = pd.cut(
                                df_heatmap['rows'] * df_heatmap['columns'],
                                bins=3,
                                labels=['Small', 'Medium', 'Large']
                            )
                            render_chart(df_heatmap, "heatmap", groupby=["uploaded_by", "size_category"],
                                       title="Uploader Heatmap")
        else:
            st.info("No data available for advanced analytics")

        st.markdown("---")

        st.subheader("📄 Datasets Data & AI Assistant")
        data_col, ai_col = st.columns([2, 1])
        
        with data_col:
            if self.df is None or self.df.empty:
                st.info("No datasets found.")
            else:
                st.dataframe(self.df, height=500)
        
        with ai_col:
            self.render_ai_panel()

        st.markdown("---")

        st.subheader("📤 Upload Dataset CSV (Same schema)")
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
                        st.success("Uploaded successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        st.markdown("---")

        st.subheader("➕ Add Dataset (Quick Add)")
        with st.form("add_dataset"):
            nm = st.text_input("Dataset name")
            rows = st.number_input("Rows", min_value=0, step=1)
            cols = st.number_input("Columns", min_value=0, step=1)
            uploaded_by = st.text_input("Uploaded by", value=self.username)
            upload_date = st.date_input("Upload date")
            add = st.form_submit_button("Add")
            if add:
                # Validate required fields
                if not nm or not nm.strip():
                    st.error("Dataset name is required.")
                elif rows <= 0:
                    st.error("Rows must be greater than 0.")
                elif cols <= 0:
                    st.error("Columns must be greater than 0.")
                elif not uploaded_by or not uploaded_by.strip():
                    st.error("Uploaded by is required.")
                else:
                    try:
                        tmpdir = Path("DATA")
                        tmpdir.mkdir(exist_ok=True)
                        tmpfile = tmpdir / \
                            f"tmp_new_dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                        pd.DataFrame([{
                            "name": nm.strip(),
                            "rows": int(rows),
                            "columns": int(cols),
                            "uploaded_by": uploaded_by.strip(),
                            "upload_date": upload_date.isoformat()
                        }]).to_csv(tmpfile, index=False)
                        load_csv_to_table(
                            str(tmpfile), "datasets_metadata", if_exists="append")
                        st.success("Dataset added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add dataset: {e}")

    def render_ai_panel(self):
        st.markdown("### 🧠 Data AI Assistant")
        
        # Info about preferences
        st.info("💡 **Tip:** You can ask for explanations, insights, or code examples. Specify your preference in your question (e.g., 'explain without code' or 'show me the code').")
        
        # Example questions
        example_questions = [
            "What is the total size of all datasets?",
            "Which user has uploaded the most datasets?",
            "Show me dataset upload trends",
            "What is the average number of rows per dataset?",
            "Analyse the dataset size distribution",
            "Which datasets have the most columns?"
        ]
        
        st.markdown("<div style='margin-bottom: 10px;'><strong style='color: #FF1493;'>💡 Example Questions:</strong></div>", unsafe_allow_html=True)
        
        # Display example questions as buttons
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_data_{i}"):
                # Automatically send the question
                history = load_ai_history(self.username, "data") or []
                save_ai_message(self.username, "data", "user", question)
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
                        for chunk in get_gemini_response(question, chat_history, "data"):
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
                        save_ai_message(self.username, "data", "assistant", full)
                    except Exception as e:
                        error_msg = f"⚠️ AI Error: {str(e)}"
                        typing_placeholder.markdown(
                            f"<div class='ai-response'><strong>AI:</strong> {error_msg}</div>", 
                            unsafe_allow_html=True
                        )
                        save_ai_message(self.username, "data", "assistant", error_msg)
                else:
                    fallback = f"[Local] Received: {question}"
                    save_ai_message(self.username, "data", "assistant", fallback)
                
                st.rerun()

        st.markdown("---")

        history = load_ai_history(self.username, "data") or []
        
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
            if "data_query" in st.session_state and st.session_state.data_query:
                st.session_state.data_send_trigger = True
        
        # Check if we need to process a message
        if st.session_state.get("data_send_trigger", False) and st.session_state.get("data_query"):
            user_message = st.session_state.data_query
            st.session_state.data_send_trigger = False
            
            try:
                save_ai_message(self.username, "data", "user", user_message)
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
                    for chunk in get_gemini_response(user_message, chat_history, "data"):
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
                    save_ai_message(self.username, "data", "assistant", full)
                except Exception as e:
                    error_msg = f"⚠️ AI Error: {str(e)}"
                    typing_placeholder.markdown(
                        f"<div class='ai-response'><strong>AI:</strong> {error_msg}</div>", 
                        unsafe_allow_html=True
                    )
                    save_ai_message(self.username, "data", "assistant", error_msg)
            else:
                fallback = f"[Local] Received: {user_message}"
                st.markdown(
                    f"<div class='ai-response'>{fallback}</div>", unsafe_allow_html=True)
                try:
                    save_ai_message(self.username, "data", "assistant", fallback)
                except Exception:
                    pass
            
            # Clear input and rerun
            st.session_state.data_query = ""
            st.rerun()
        
        # Input and send
        q = st.text_input(
            "Ask the Data AI assistant... (Press Enter to send)", 
            key="data_query",
            on_change=send_message
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Send", key="data_send"):
                send_message()
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear", key="data_clear"):
                try:
                    delete_ai_history(self.username, "data")
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
    DataScienceDashboard().run()
