import bcrypt
import os
from pathlib import Path
from app.data.db import connect_database

USERS_TXT_PATH = Path("DATA/users.txt")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def register_user(username: str, password: str, role: str = "user"):
    """Register a new user with bcrypt hashing."""
    try:
        conn = connect_database()
        cur = conn.cursor()

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

        # Append user to users.txt file
        try:
            # Ensure DATA directory exists
            USERS_TXT_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Append in format: username,password_hash,role
            with open(USERS_TXT_PATH, "a", encoding="utf-8") as fh:
                fh.write(f"{username},{pw_hash},{role}\n")
        except Exception as file_error:
            # Log warning but don't fail registration
            print(f"Warning: Could not write to users.txt: {file_error}")

        return True, "User registered."

    except Exception as e:
        return False, f"Registration error: {e}"


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

        # Verify password against stored hash
        if not verify_password(password, stored_hash):
            return False, "Incorrect password.", None, None

        token = f"TOKEN::{username}"
        return True, "Login successful.", token, role

    except Exception as e:
        return False, f"Login error: {e}", None, None


def migrate_users_from_file():
    """Import users from DATA/users.txt, hashing any plain text passwords if needed."""
    if not USERS_TXT_PATH.exists():
        return 0

    count = 0

    with open(USERS_TXT_PATH, "r") as fh:
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue

            username, password_or_hash, role = parts[0], parts[1], parts[2]

            if password_or_hash.startswith("$2b$"):
                pw_hash = password_or_hash
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


def get_valid_avatar_path(username: str, avatar_path: str = None):
    """Get a valid avatar path, checking if file exists and correcting path if needed.
    
    Args:
        username: The username to get avatar for
        avatar_path: Optional avatar path from database
        
    Returns:
        Valid file path if exists, None otherwise
    """
    if not avatar_path:
        return None
    
    # Check if the stored path exists
    if os.path.exists(avatar_path):
        return avatar_path
    
    # Try to construct correct path relative to current working directory
    filename = os.path.basename(avatar_path)
    image_folder = Path("app/user_images")
    correct_path = image_folder / filename
    
    if correct_path.exists():
        # Update database with correct path
        abs_path = os.path.abspath(str(correct_path)).replace("\\", "/")
        try:
            conn = connect_database()
            cur = conn.cursor()
            cur.execute("UPDATE users SET avatar = ? WHERE username = ?",
                        (abs_path, username))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not update avatar path in database: {e}")
        return str(correct_path)
    
    return None


def update_user_profile_image(username: str, image_path: str):
    """Store absolute avatar path for use in image tags."""
    try:
        abs_path = os.path.abspath(image_path)
        abs_path = abs_path.replace("\\", "/")

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


def remove_user_profile_image(username: str):
    """Remove user's profile picture from database and delete file.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get current avatar path before removing
        user = get_user_by_username(username)
        avatar_path = user.get("avatar") if user else None

        # Remove from database
        conn = connect_database()
        cur = conn.cursor()
        cur.execute("UPDATE users SET avatar = NULL WHERE username = ?",
                    (username,))
        conn.commit()
        conn.close()

        # Delete file if it exists
        if avatar_path and os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
            except Exception as file_error:
                # Log warning but don't fail
                print(f"Warning: Could not delete avatar file: {file_error}")

        return True, "Profile picture removed successfully."
    except Exception as e:
        print("remove_user_profile_image error:", e)
        return False, f"Failed to remove profile picture: {str(e)}"


class UserService:
    """Object-oriented wrapper for user operations."""

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
