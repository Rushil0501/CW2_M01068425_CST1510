"""
User-level business logic: register, login, migrate, and validation.
Includes Week 7 Challenges: Lockout, Strength Check, Session Tokens.
"""
from app.data.users import get_user_by_username, insert_user
from app.data.db import connect_database
import bcrypt
import re
import time
import secrets
from pathlib import Path

DATA_DIR = Path("DATA")
USERS_TXT = DATA_DIR / "users.txt"

# --- Challenge 3: In-Memory Lockout Storage ---
FAILED_LOGIN_LIMIT = 3
LOCKOUT_DURATION = 300  # 5 minutes
failed_login_attempts = {}  # {username: (count, timestamp)}

# --- Helper Functions (Moved from auth.py) ---


def validate_username(username):
    """Moved from Week 7 auth.py"""
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters."
    if not username.isalnum():
        return False, "Username must contain only letters and numbers."
    return True, ""


def validate_password(password):
    """Moved from Week 7 auth.py"""
    if not (6 <= len(password) <= 50):
        return False, "Password must be between 6 and 50 characters."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def check_password_strength(password):
    """Challenge 1: Returns Weak, Medium, or Strong."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?:{}|<>]", password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    return "Strong"


def create_session(username):
    """Challenge 4: Generate a session token."""
    token = secrets.token_hex(16)
    # In a real app, you'd save this to a DB. For now, just returning it.
    return token


def _record_failed_login(username):
    """Internal helper to track failed logins."""
    current_time = time.time()
    if username not in failed_login_attempts:
        failed_login_attempts[username] = (1, current_time)
    else:
        count, _ = failed_login_attempts[username]
        failed_login_attempts[username] = (count + 1, current_time)

# --- Main Service Functions ---


def register_user(username, password, role='user'):
    """Register user with validation and hashing."""

    # 1. Validate Inputs (Your Week 7 Logic)
    valid_user, msg = validate_username(username)
    if not valid_user:
        return False, msg

    valid_pass, msg = validate_password(password)
    if not valid_pass:
        return False, msg

    # 2. Check Database (Replaces user_exists logic)
    if get_user_by_username(username):
        return False, f"Username '{username}' already exists."

    # 3. Hash Password
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

    # 4. Insert into DB (Replaces file writing)
    new_id = insert_user(username, hashed, role)
    if new_id:
        strength = check_password_strength(password)
        return True, f"User registered! (Password Strength: {strength})"
    return False, "Registration failed (Database Error)."


# app/services/user_service.py (Partial Update)

# ... keeps existing imports and helper functions ...

# app/services/user_service.py (Partial Update)

# ... keeps existing imports and helper functions ...

# app/services/user_service.py (Partial Update)

# ... keeps existing imports and helper functions ...

# app/services/user_service.py (Update login_user)

def login_user(username, password):
    """Authenticate user and return their role."""

    # 1. Check Lockout (Existing Logic)
    if username in failed_login_attempts:
        count, last_attempt = failed_login_attempts[username]
        if count >= FAILED_LOGIN_LIMIT:
            time_since = time.time() - last_attempt
            if time_since < LOCKOUT_DURATION:
                remaining = int(LOCKOUT_DURATION - time_since)
                # Return 4 values: Success, Msg, Token, Role
                return False, f"Locked out. Wait {remaining}s.", None, None
            else:
                del failed_login_attempts[username]

    # 2. Fetch User
    row = get_user_by_username(username)
    if not row:
        _record_failed_login(username)
        return False, "User not found.", None, None

    # 3. Verify Password
    stored_hash = row["password_hash"]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        if username in failed_login_attempts:
            del failed_login_attempts[username]

        # --- NEW: Retrieve Role and Create Token ---
        token = create_session(username)
        user_role = row["role"]  # Fetch the role column

        return True, "Login Successful", token, user_role

    # 4. Handle Failure
    _record_failed_login(username)
    return False, "Incorrect password.", None, None


def migrate_users_from_file(filepath: Path = USERS_TXT):
    """Migrate users from users.txt to DB."""
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
                # Handle optional role from Week 7 file format
                role = parts[2].strip() if len(parts) >= 3 else 'user'
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cur.rowcount > 0:
                        migrated += 1
                except Exception:
                    continue
    conn.commit()
    conn.close()
    return migrated
