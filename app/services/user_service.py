import bcrypt
import os
from pathlib import Path
from app.data.db import connect_database

USERS_TXT_PATH = Path("DATA/users.txt")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ------------------------------------------------------------
# REGISTER USER
# ------------------------------------------------------------
def register_user(username: str, password: str, role: str = "user"):
    """Register a new user with bcrypt hashing."""
    try:
        conn = connect_database()
        cur = conn.cursor()

        # Check existing
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return False, "Username already exists."

        pw_hash = hash_password(password)

        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, pw_hash, role),
        )

        conn.commit()
        conn.close()
        return True, "User registered."

    except Exception as e:
        return False, f"Registration error: {e}"


# ------------------------------------------------------------
# LOGIN USER
# ------------------------------------------------------------
def login_user(username: str, password: str):
    """Authenticate user using bcrypt."""
    try:
        conn = connect_database()
        cur = conn.cursor()

        cur.execute(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return False, "User not found.", None, None

        stored_hash, role = row[0], row[1]

        # Compare bcrypt hash
        if not verify_password(password, stored_hash):
            return False, "Incorrect password.", None, None

        token = f"TOKEN::{username}"
        return True, "Login successful.", token, role

    except Exception as e:
        return False, f"Login error: {e}", None, None


# ------------------------------------------------------------
# MIGRATE USERS FROM users.txt
# ------------------------------------------------------------
def migrate_users_from_file():
    """
    users.txt contains:
    username, bcrypt_hash, role

    If the second field starts with `$2b$` → already bcrypt → store directly.
    If not → treat as plain password → hash it into bcrypt.
    """
    if not USERS_TXT_PATH.exists():
        return 0

    count = 0

    with open(USERS_TXT_PATH, "r") as fh:
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue

            username, password_or_hash, role = parts[0], parts[1], parts[2]

            # Check if bcrypt hash already
            if password_or_hash.startswith("$2b$"):
                pw_hash = password_or_hash  # use directly
            else:
                pw_hash = hash_password(password_or_hash)

            try:
                conn = connect_database()
                cur = conn.cursor()

                cur.execute(
                    "SELECT id FROM users WHERE username = ?", (username,))
                exists = cur.fetchone()

                if not exists:
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, pw_hash, role),
                    )
                    conn.commit()
                    count += 1

                conn.close()
            except Exception as e:
                print("Migration error:", e)

    return count


# ------------------------------------------------------------
# PROFILE HELPERS
# ------------------------------------------------------------
def get_user_by_username(username: str):
    try:
        conn = connect_database()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, role, avatar, created_at FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "username": row[0],
            "role": row[1],
            "avatar": row[2],
            "created_at": row[3],
        }

    except Exception as e:
        print("get_user_by_username error:", e)
        return None


def update_user_profile_image(username: str, image_path: str):
    """
    Save avatar path using a fully absolute, normalized path.
    Streamlit needs correct absolute paths for <img src="..."> tags.
    """
    try:
        # Convert to full absolute path
        abs_path = os.path.abspath(image_path)
        abs_path = abs_path.replace("\\", "/")  # Normalize for HTML

        conn = connect_database()
        cur = conn.cursor()
        cur.execute("UPDATE users SET avatar = ? WHERE username = ?",
                    (abs_path, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("update_user_profile_image error:", e)
        return False

# ============================================================
# OOP SERVICE LAYER (WRAPS EXISTING FUNCTIONS)
# ============================================================


class UserService:
    """
    Object-Oriented wrapper for user-related operations.
    Existing procedural functions are reused internally.
    """

    def register(self, username: str, password: str, role: str = "user"):
        return register_user(username, password, role)

    def login(self, username: str, password: str):
        return login_user(username, password)

    def get_user(self, username: str):
        return get_user_by_username(username)

    def update_avatar(self, username: str, image_path: str) -> bool:
        return update_user_profile_image(username, image_path)

    def migrate_users(self):
        return migrate_users_from_file()
