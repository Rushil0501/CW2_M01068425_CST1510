from app.data.db import connect_database
import pandas as pd


def insert_ticket(priority, description, status, assigned_to, created_at, resolution_time_hours, ticket_id=None):
    """Insert a new ticket; ID defaults to database-generated."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_ticket_by_id(ticket_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_ticket_status(ticket_id, new_status):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
                (new_status, ticket_id))
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def delete_ticket(ticket_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows


def get_all_tickets():
    """Return all tickets as a DataFrame."""
    conn = connect_database()
    # logical ordering: High priority first, then by date
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY created_at DESC", conn)
    conn.close()
    return df

class TicketService:
    """Handle IT support tickets."""

    def create_ticket(self, priority, description, status, assigned_to, created_at, resolution_time_hours):
        return insert_ticket(priority, description, status, assigned_to, created_at, resolution_time_hours)

    def all_tickets(self):
        return get_all_tickets()

    def get(self, ticket_id):
        return get_ticket_by_id(ticket_id)

    def update_status(self, ticket_id, new_status):
        return update_ticket_status(ticket_id, new_status)

    def delete(self, ticket_id):
        return delete_ticket(ticket_id)
