import streamlit as st
from app.services.ai_service import get_gemini_response
from DATA.ai_history import load_history, save_message


def render_ai_console(role):
    username = st.session_state.username

    st.markdown("---")

    ai_names = {
        "cyber": "🕵️‍♂️ Cybersecurity AI",
        "it": "🛠️ IT Support AI",
        "data": "🧠 Data Lab AI",
        "admin": "⚡ Admin AI"
    }

    st.subheader(ai_names.get(role, "⚡ AI Assistant"))

    # 1. Load persistent history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": msg_role, "content": content}
            for msg_role, content in load_history(username, role)
        ]

    # 2. Display history
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    # 3. Input box
    with st.form("ai_chat_form", clear_on_submit=True):
        prompt = st.text_input("Ask something...", "")
        send = st.form_submit_button("Send")

        if send and prompt:
            # Save user message
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            save_message(username, role, "user", prompt)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                final = ""

                stream = get_gemini_response(
                    prompt, st.session_state.messages, role)
                for chunk in stream:
                    if hasattr(chunk, "text"):
                        final += chunk.text
                        placeholder.write(final + "▌")

                placeholder.write(final)

            # Save assistant message
            st.session_state.messages.append(
                {"role": "assistant", "content": final})
            save_message(username, role, "assistant", final)
