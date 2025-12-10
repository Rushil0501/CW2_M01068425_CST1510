def create_users_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        avatar TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()


def create_cyber_incidents_table(conn):
    """Matches cyber_incidents.csv exactly."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        incident_id INTEGER PRIMARY KEY,
        timestamp TEXT,
        severity TEXT,
        category TEXT,
        status TEXT,
        description TEXT
    )
    """)
    conn.commit()


def create_datasets_metadata_table(conn):
    """Matches datasets_metadata.csv exactly."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        dataset_id INTEGER PRIMARY KEY,
        name TEXT,
        rows INTEGER,
        columns INTEGER,
        uploaded_by TEXT,
        upload_date TEXT
    )
    """)
    conn.commit()


def create_it_tickets_table(conn):
    """Matches it_tickets.csv exactly."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_tickets (
        ticket_id INTEGER PRIMARY KEY,
        priority TEXT,
        description TEXT,
        status TEXT,
        assigned_to TEXT,
        created_at TEXT,
        resolution_time_hours INTEGER
    )
    """)
    conn.commit()


def create_ai_chat_history_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        message_role TEXT NOT NULL,   -- 'user' or 'assistant'
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    conn.commit()


def create_all_tables(conn):
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    create_ai_chat_history_table(conn)
