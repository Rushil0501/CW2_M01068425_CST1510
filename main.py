"""
Demo script to setup database, migrate users, load CSVs and run sample CRUD.
Run: python main.py
"""
from app.data.db import connect_database, DB_PATH
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident, get_incidents_by_type_count
from app.data.datasets import load_csv_to_table
from pathlib import Path
import pandas as pd

DATA_DIR = Path("DATA")


def setup_database_complete():
    """Create DB, tables, migrate users and load CSVs."""
    print("\n[1/5] Connecting to database")
    conn = connect_database()
    print("[2/5] Creating tables")
    create_all_tables(conn)

    print("[3/5] Migrating users from users.txt (if exists)")
    migrated = migrate_users_from_file()
    print(f"    Migrated users: {migrated}")

    # Load CSVs if present
    print("[4/5] Loading CSV files (if present)")
    csv_files = {
        "cyber_incidents.csv": ("DATA/cyber_incidents.csv", "cyber_incidents"),
        "datasets_metadata.csv": ("DATA/datasets_metadata.csv", "datasets_metadata"),
        "it_tickets.csv": ("DATA/it_tickets.csv", "it_tickets")
    }
    total_loaded = 0
    for name, (path, table) in csv_files.items():
        p = Path(path)
        if p.exists():
            try:
                rows = load_csv_to_table(p, table, if_exists='append')
                print(f"    Loaded {rows} rows into {table} from {name}")
                total_loaded += rows
            except Exception as e:
                print(f"    Failed loading {name}: {e}")
        else:
            print(f"    {name} not found, skipping.")

    print("[5/5] Setup verification")
    cur = conn.cursor()
    for t in ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
        except Exception:
            cnt = 0
        print(f"    {t}: {cnt} rows")
    conn.close()
    print(f"\nDatabase created at: {DB_PATH.resolve()}")


def demo_crud_and_auth():
    """Create a user, login, insert incident, query and clean up."""
    print("\n--- DEMO: auth and incident CRUD ---")
    ok, msg = register_user("alice_demo", "SecurePass123!", "analyst")
    print("Register:", msg)

    ok, msg = login_user("alice_demo", "SecurePass123!")
    print("Login:", msg)

    iid = insert_incident(999999,
                          "2024-11-05",
                          "High",
                          "Phishing",
                          "Open",
                          "Suspicious email seen"
                          "alice_demo")
    print("Inserted incident id:", iid)

    df = get_all_incidents()
    print("Total incidents in DB:", len(df))

    updated = update_incident_status(iid, "Resolved")
    print("Status update affected:", updated)

    deleted = delete_incident(iid)
    print("Deleted incident rows:", deleted)

    # show analytical query
    df_types = get_incidents_by_type_count()
    print("\nIncidents by type sample:")
    print(df_types.head())


if __name__ == "__main__":
    setup_database_complete()
    demo_crud_and_auth()
