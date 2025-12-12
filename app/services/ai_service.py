import google.generativeai as genai
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from app.data.db import DB_PATH

from app.data.incidents import get_all_incidents
from app.data.tickets import get_all_tickets
from app.data.datasets import list_datasets


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
Provide clear explanations and insights about datasets. Only provide code snippets when the user explicitly asks for code or programming examples. Otherwise, focus on analytical insights, patterns, and recommendations."""
    }
    return personalities.get(role, "You are a helpful enterprise assistant.")


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


def get_gemini_response(user_prompt, chat_history, role):
    """Return a generator that yields response chunks for streaming."""
    # Helper class for error messages
    class ErrorChunk:
        def __init__(self, text):
            self.text = text
    
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            yield ErrorChunk("⚠️ Error: Missing GOOGLE_API_KEY in secrets.toml. Please add your Google API key to .streamlit/secrets.toml")
            return
        genai.configure(api_key=api_key)
    except Exception as e:
        yield ErrorChunk(f"⚠️ Error: Failed to configure API - {str(e)}")
        return

    try:
        # Try to find an available model
        model = None
        last_error = None
        
        # First, try to list available models
        try:
            models = genai.list_models()
            available_models = []
            for m in models:
                if hasattr(m, 'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
                    model_name = m.name
                    # Remove 'models/' prefix if present
                    if model_name.startswith('models/'):
                        model_name = model_name[7:]
                    available_models.append(model_name)
            
            # Try available Gemini models first
            if available_models:
                for model_name in available_models:
                    if 'gemini' in model_name.lower():
                        try:
                            model = genai.GenerativeModel(model_name)
                            break
                        except:
                            continue
        except:
            pass
        
        # If no model found, try common names
        if model is None:
            model_names = ["gemini-pro", "gemini-1.5-pro"]
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
        
        if model is None:
            error_msg = f"⚠️ Error: Could not initialize Gemini model.\n\nError: {last_error or 'Unknown error'}\n\nPlease check:\n1. Your API key is valid and has proper permissions\n2. The Gemini API is enabled in your Google Cloud project\n3. Try using 'gemini-pro' model name"
            yield ErrorChunk(error_msg)
            return

        gemini_history = []

        system_instruction = (
            get_system_prompt(role)
            + "\n\n"
            + get_data_context(role)
            + "\n\nUse only the facts from the above data."
        )

        gemini_history.append({"role": "user", "parts": [system_instruction]})
        gemini_history.append(
            {"role": "model", "parts": ["Understood. Using live database context."]})

        for msg in chat_history:
            role_map = {"user": "user", "assistant": "model"}
            gemini_history.append({
                "role": role_map.get(msg["role"], "user"),
                "parts": [msg["content"]]
            })

        chat = model.start_chat(history=gemini_history)
        stream = chat.send_message(user_prompt, stream=True)

        for chunk in stream:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk

    except Exception as e:
        yield ErrorChunk(f"⚠️ AI Error: {str(e)}")


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

class AIService:
    """Handle AI responses with role-based prompts."""

    def ask(self, username, message, role):
        history = load_chat_history(username, role)
        save_chat_message(username, role, "user", message)
        response = get_gemini_response(message, history, role)
        save_chat_message(username, role, "assistant", response)
        return response
