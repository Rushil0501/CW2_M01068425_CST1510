"""
User-level business logic: register, login, migrate from users.txt
"""
from app.data.users import get_user_by_username, insert_user, list_users
from app.data.db import connect_database
import bcrypt
from pathlib import Path

DATA_DIR = Path("DATA")
USERS_TXT = DATA_DIR / "users.txt"


def register_user(username, password, role='user'):
    """Register user with bcrypt hashing. Returns (success, message)."""
    # check exists
    if get_user_by_username(username):
        return False, f"Username '{username}' already exists."

    # hash password
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

    new_id = insert_user(username, hashed, role)
    if new_id:
        return True, f"User '{username}' registered."
    return False, "Registration failed."


def login_user(username, password):
    """Authenticate user. Returns (success, message)."""
    row = get_user_by_username(username)
    if not row:
        return False, "User not found."

    stored_hash = row["password_hash"]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Welcome, {username}!"
    return False, "Incorrect password."


def migrate_users_from_file(filepath: Path = USERS_TXT):
    """
    Migrate users from users.txt (format: username,password_hash,role)
    Returns number of migrated users.
    """
    if not filepath.exists():
        return 0
    conn = connect_database()
    cur = conn.cursor()
    migrated = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0].strip()
                password_hash = parts[1].strip()
                role = parts[2].strip() if len(parts) >= 3 else 'user'
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cur.rowcount > 0:
                        migrated += 1
                except Exception:
                    # skip problematic entries
                    continue
    conn.commit()
    conn.close()
    return migrated
