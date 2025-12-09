from app.data.db import connect_database, DB_PATH
from app.data.schema import create_all_tables
from app.services.user_service import register_user, migrate_users_from_file
from app.data.datasets import load_csv_to_table
from pathlib import Path


DATA_DIR = Path("DATA")


def setup_database_complete():
    """Create the database, migrate users, and seed CSV data."""
    print("\n" + "="*50)
    print(" STARTING DATABASE SETUP ")
    print("="*50)

    print("\n[1/5] Connecting to database...")
    conn = connect_database()

    print("[2/5] Creating tables...")
    create_all_tables(conn)
    print("    -> All tables created (including AI chat history)")

    print("[3/5] Migrating users from users.txt...")
    migrated = migrate_users_from_file()
    print(f"    -> Migrated {migrated} users")

    # Load CSVs if present
    print("[4/5] Loading CSV files...")
    csv_files = {
        "cyber_incidents.csv": ("DATA/cyber_incidents.csv", "cyber_incidents"),
        "datasets_metadata.csv": ("DATA/datasets_metadata.csv", "datasets_metadata"),
        "it_tickets.csv": ("DATA/it_tickets.csv", "it_tickets")
    }

    for name, (path, table) in csv_files.items():
        p = Path(path)
        if p.exists():
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]

                if count == 0:
                    rows = load_csv_to_table(p, table, if_exists='append')
                    print(f"    -> Loaded {rows} rows into {table}")
                else:
                    print(
                        f"    -> {table} already has {count} rows. Skipping CSV load.")
            except Exception as e:
                print(f"    -> Failed loading {name}: {e}")
        else:
            print(f"    -> {name} not found. Skipping.")

    print("[5/5] Creating Demo Admin User...")
    success, msg = register_user("admin", "Admin123!", "admin")
    print(f"    -> {msg}")

    conn.close()
    print("\n" + "="*50)
    print(f" SETUP COMPLETE")
    print(f" Database: {DB_PATH.resolve()}")
    print(" You can now run: streamlit run Home.py")
    print("="*50)


if __name__ == "__main__":
    setup_database_complete()
