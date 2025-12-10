from app.data.db import connect_database
import pandas as pd
from pathlib import Path


def load_csv_to_table(csv_path, table_name, if_exists="append"):
    """Load a CSV into a database table."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    conn = connect_database()
    df.to_sql(
        name=table_name,
        con=conn,
        if_exists=if_exists,
        index=False
    )
    rows = len(df)
    conn.close()
    return rows


def list_datasets():
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY dataset_id ASC", conn)
    conn.close()
    return df

class DatasetService:
    """Handle dataset operations."""

    def load_csv(self, csv_path, table_name, if_exists="append"):
        return load_csv_to_table(csv_path, table_name, if_exists)

    def list_all(self):
        return list_datasets()
