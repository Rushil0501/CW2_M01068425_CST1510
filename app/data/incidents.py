from app.data.db import connect_database
import pandas as pd


def insert_incident(timestamp, severity, category, status, description, incident_id=None):
    """Insert a new incident. ID defaults to database-generated if not provided."""
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cyber_incidents
        (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_all_incidents():
    """Return all incidents as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY incident_id ASC", conn)
    conn.close()
    return df


def get_incident_by_id(incident_id):
    """Return a single incident by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_incident_status(incident_id, new_status):
    """Update an incident status."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
                (new_status, incident_id))
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows


def delete_incident(incident_id):
    """Delete an incident by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows


def get_incidents_by_type_count():
    """Count incidents by category."""
    conn = connect_database()
    query = """
    SELECT category, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY category
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_high_severity_by_status():
    """Count high severity incidents by status."""
    conn = connect_database()
    query = """
    SELECT status, COUNT(*) AS count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

class IncidentService:
    """Handle cybersecurity incidents."""

    def add_incident(self, timestamp, severity, category, status, description):
        return insert_incident(timestamp, severity, category, status, description)

    def all_incidents(self):
        return get_all_incidents()

    def get_by_id(self, incident_id):
        return get_incident_by_id(incident_id)

    def update_status(self, incident_id, status):
        return update_incident_status(incident_id, status)

    def delete(self, incident_id):
        return delete_incident(incident_id)

    def count_by_category(self):
        return get_incidents_by_type_count()

    def high_severity_by_status(self):
        return get_high_severity_by_status()
