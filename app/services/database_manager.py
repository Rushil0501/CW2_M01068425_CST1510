from app.data.db import connect_database


class DatabaseManager:
    """
    Central database handler (OOP).
    """

    def get_connection(self):
        return connect_database()
