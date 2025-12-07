import google.generativeai as genai
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from app.data.db import DB_PATH
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

# --- IMPORT LIVE DATA FUNCTIONS ---
from app.data.incidents import get_all_incidents
from app.data.tickets import get_all_tickets
from app.data.datasets import list_datasets


# ==========================================================
#                 DATABASE CHAT HISTORY
# ==========================================================

def save_chat_message(username, role, sender, content):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ai_chat_history (username, role, message_role, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (username, role, sender, content, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def load_chat_history(username, role):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT message_role, content, timestamp
        FROM ai_chat_history
        WHERE username = ? AND role = ?
        ORDER BY id ASC
    """, (username, role))

    rows = cur.fetchall()
    conn.close()

    return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]


def clear_chat_history(username, role):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM ai_chat_history
        WHERE username = ? AND role = ?
    """, (username, role))

    conn.commit()
    conn.close()


# ==========================================================
#                 ROLE PERSONALITIES
# ==========================================================

def get_system_prompt(role):
    personalities = {
        "cyber": """You are a Tier-3 Cyber Security Analyst.
Focus on: Threat hunting, CVE analysis, incident response, MITRE ATT&CK, log analysis.
Be concise, technical, and evidence-based.""",

        "it": """You are a Senior IT Support Manager (ITIL Certified).
Focus on: Hardware diagnostics, troubleshooting, network issues, SLAs.
Be clear, helpful, and professional.""",

        "data": """You are a Lead Data Scientist.
Focus on: Pandas, NumPy, cleaning, statistics, ML concepts.
Provide code snippets when helpful."""
    }
    return personalities.get(role, "You are a helpful enterprise assistant.")


# ==========================================================
#                 DATA CONTEXT (LIVE DATABASE)
# ==========================================================

def get_data_context(role):
    try:
        if role == "cyber":
            df = get_all_incidents()
        elif role == "it":
            df = get_all_tickets()
        elif role == "data":
            df = list_datasets()
        else:
            return ""

        if df.empty:
            return "\n[DATABASE CONTEXT: No data found]\n"

        return f"\n[DATABASE CONTEXT - TOP 50 ROWS]\n{df.head(50).to_csv(index=False)}\n"

    except Exception as e:
        return f"\n[ERROR FETCHING DATA]: {e}\n"


# ==========================================================
#                 GEMINI RESPONSE HANDLER
# ==========================================================

def get_gemini_response(user_prompt, chat_history, role):
    # 1. API key check
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        return "⚠️ Error: Missing or invalid GOOGLE_API_KEY in secrets.toml"

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Build history
        gemini_history = []

        # System + Data Context
        system_instruction = (
            get_system_prompt(role)
            + "\n\n"
            + get_data_context(role)
            + "\n\nUse only the facts from the above data."
        )

        gemini_history.append({"role": "user", "parts": [system_instruction]})
        gemini_history.append(
            {"role": "model", "parts": ["Understood. Using live database context."]})

        # Add past chat
        for msg in chat_history:
            role_map = {"user": "user", "assistant": "model"}
            gemini_history.append({
                "role": role_map.get(msg["role"], "user"),
                "parts": [msg["content"]]
            })

        chat = model.start_chat(history=gemini_history)
        stream = chat.send_message(user_prompt, stream=True)

        full_response = ""
        for chunk in stream:
            if hasattr(chunk, "text"):
                full_response += chunk.text

        return full_response

    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ==========================================================
#                 PUBLIC FUNCTIONS FOR DASHBOARDS
# ==========================================================

def cyber_ai_chat(username, message):
    role = "cyber"
    history = load_chat_history(username, role)
    save_chat_message(username, role, "user", message)

    response = get_gemini_response(message, history, role)
    save_chat_message(username, role, "assistant", response)

    return response


def data_ai_chat(username, message):
    role = "data"
    history = load_chat_history(username, role)
    save_chat_message(username, role, "user", message)

    response = get_gemini_response(message, history, role)
    save_chat_message(username, role, "assistant", response)

    return response


def it_ai_chat(username, message):
    role = "it"
    history = load_chat_history(username, role)
    save_chat_message(username, role, "user", message)

    response = get_gemini_response(message, history, role)
    save_chat_message(username, role, "assistant", response)

    return response

# =========================================================
# OOP AI SERVICE
# =========================================================


class AIService:
    """
    Handles AI responses with role-based intelligence.
    """

    def ask(self, username, message, role):
        history = load_chat_history(username, role)
        save_chat_message(username, role, "user", message)
        response = get_gemini_response(message, history, role)
        save_chat_message(username, role, "assistant", response)
        return response
