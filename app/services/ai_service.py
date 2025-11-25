import google.generativeai as genai
import streamlit as st
import pandas as pd
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

# --- IMPORT DATA FUNCTIONS ---
# We need these to fetch the live data from your DB
from app.data.incidents import get_all_incidents
from app.data.tickets import get_all_tickets
from app.data.datasets import list_datasets

# Helper class to mimic Gemini response chunk


class MockChunk:
    def __init__(self, text):
        self.text = text


def get_system_prompt(role):
    """Returns the base personality."""
    prompts = {
        "cyber": """You are a Tier-3 Cyber Security Analyst. 
                   Focus on: Threat hunting, CVE analysis, incident response, and NIST frameworks. 
                   Be concise, technical, and paranoid.""",

        "it":    """You are a Senior IT Service Manager (ITIL Certified).
                   Focus on: Hardware troubleshooting, network protocols, ticket prioritization, and SLAs.
                   Be helpful, patient, and ask clarifying questions.""",

        "data":  """You are a Lead Data Scientist.
                   Focus on: Python (Pandas/NumPy), statistical analysis, data cleaning, and ML models.
                   Always provide code snippets when asked about data transformation."""
    }
    return prompts.get(role, "You are a helpful enterprise assistant.")


def get_data_context(role):
    """
    Fetches the actual data from the database based on the role
    and converts it to a CSV-string so the AI can 'read' it.
    """
    context_str = ""

    try:
        if role == 'cyber':
            df = get_all_incidents()
            if not df.empty:
                # Convert to CSV string (limit to top 50 rows to save tokens)
                data_str = df.head(50).to_csv(index=False)
                context_str = f"\n\n[LIVE DATABASE CONTEXT - INCIDENTS TABLE]\n{data_str}\n"
            else:
                context_str = "\n\n[LIVE DATABASE CONTEXT]\nNo incidents found in database.\n"

        elif role == 'it':
            df = get_all_tickets()
            if not df.empty:
                data_str = df.head(50).to_csv(index=False)
                context_str = f"\n\n[LIVE DATABASE CONTEXT - IT TICKETS TABLE]\n{data_str}\n"
            else:
                context_str = "\n\n[LIVE DATABASE CONTEXT]\nNo tickets found.\n"

        elif role == 'data':
            df = list_datasets()
            if not df.empty:
                data_str = df.head(50).to_csv(index=False)
                context_str = f"\n\n[LIVE DATABASE CONTEXT - AVAILABLE DATASETS]\n{data_str}\n"
            else:
                context_str = "\n\n[LIVE DATABASE CONTEXT]\nNo datasets uploaded yet.\n"

    except Exception as e:
        context_str = f"\n\n[SYSTEM ERROR FETCHING DATA]: {str(e)}\n"

    return context_str


def get_gemini_response(user_prompt, chat_history, role):
    """
    Sends message + Data Context to Gemini.
    """
    # 1. Check Key
    api_key = None
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
        else:
            return iter([MockChunk("⚠️ Error: GOOGLE_API_KEY is missing in secrets.toml")])
    except (StreamlitSecretNotFoundError, FileNotFoundError):
        return iter([MockChunk("⚠️ Error: The .streamlit/secrets.toml file is missing.")])

    # 2. Configure
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return iter([MockChunk(f"⚠️ Configuration Error: {str(e)}")])

    # 3. Generate Response
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- BUILD HISTORY WITH DATA CONTEXT ---
        gemini_history = []

        # A. Get the Personality
        base_prompt = get_system_prompt(role)

        # B. Get the Live Data (The "Link" to CSVs)
        data_context = get_data_context(role)

        # C. Combine them into the System Instruction
        full_system_instruction = f"{base_prompt}\n{data_context}\n\nINSTRUCTION: Use the provided Database Context above to answer user questions factually. If the data is empty, say so."

        gemini_history.append(
            {'role': 'user', 'parts': [full_system_instruction]})
        gemini_history.append({'role': 'model', 'parts': [
                              "Understood. I have access to the live database context and will use it to answer."]})

        # D. Add Conversation History
        for msg in chat_history:
            role_map = {'user': 'user', 'assistant': 'model'}
            gemini_history.append({
                'role': role_map.get(msg['role'], 'user'),
                'parts': [msg['content']]
            })

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_prompt, stream=True)
        return response

    except Exception as e:
        return iter([MockChunk(f"⚠️ AI Connection Error: {str(e)}")])
