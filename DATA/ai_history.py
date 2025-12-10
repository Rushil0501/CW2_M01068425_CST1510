from app.data.db import connect_database
from datetime import datetime


def load_history(username, role):
    """
    Returns chat history as a list of dictionaries:
    {
        "role": "user" or "assistant",
        "content": "...",
        "timestamp": "..."
    }
    """
    conn = connect_database()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT message_role, content, timestamp
            FROM ai_chat_history
            WHERE username = ? AND role = ?
            ORDER BY id ASC
        """, (username, role))

        rows = cur.fetchall()

        history = []
        for r in rows:
            history.append({
                "role": r[0],         # message_role
                "content": r[1],      # content
                "timestamp": r[2],    # timestamp
            })
        return history

    except Exception as e:
        print("Error loading history:", e)
        return []
    finally:
        conn.close()


def save_message(username, role, message_role, content):
    """
    Saves one chat message to DB.
    """
    conn = connect_database()
    cur = conn.cursor()
    try:
        ts = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO ai_chat_history (username, role, message_role, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (username, role, message_role, content, ts))
        conn.commit()
    except Exception as e:
        print("Error saving message:", e)
    finally:
        conn.close()


def delete_history(username, role):
    """
    Deletes all chat history for a user & role.
    """
    conn = connect_database()
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM ai_chat_history
            WHERE username = ? AND role = ?
        """, (username, role))
        conn.commit()
    except Exception as e:
        print("Error deleting history:", e)
    finally:
        conn.close()

# ============================================================
# OOP SERVICE
# ============================================================


class AIHistoryService:
    """
    Manages AI chat history.
    """

    def load(self, username, role):
        return load_history(username, role)

    def save(self, username, role, message_role, content):
        save_message(username, role, message_role, content)

    def clear(self, username, role):
        delete_history(username, role)
