from app.data.db import connect_database
import sqlite3


def get_user_by_username(username):
    """Return user row for given username, or None if not found."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, role, avatar, created_at FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def insert_user(username, password_hash, role='user'):
    """Insert a new user into users table."""
    conn = connect_database()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        inserted_id = cur.lastrowid
    except sqlite3.IntegrityError:
        inserted_id = None
    finally:
        conn.close()
    return inserted_id


def list_users():
    """Return list of all users as rows."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows
