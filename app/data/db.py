from pathlib import Path
import sqlite3

# path to DB file in DATA folder
DB_PATH = Path("DATA") / "intelligence_platform.db"


def connect_database(db_path: Path = DB_PATH):
    """Return a sqlite3 connection object."""
    # ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    # use row_factory for nicer row access if needed
    conn.row_factory = sqlite3.Row
    return conn
