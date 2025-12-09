from app.data.db import connect_database


class DatabaseManager:
    """Provide database connections."""

    def get_connection(self):
        return connect_database()
