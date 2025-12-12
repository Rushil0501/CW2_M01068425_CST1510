from pathlib import Path
import sqlite3

# Database file path in DATA folder
DB_PATH = Path("DATA") / "intelligence_platform.db"


def connect_database(db_path: Path = DB_PATH):
    """Return a SQLite3 connection object."""
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    # Use row_factory for easier row access
    conn.row_factory = sqlite3.Row
    return conn
