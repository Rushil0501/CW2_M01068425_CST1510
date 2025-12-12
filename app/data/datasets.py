from app.data.db import connect_database
import pandas as pd
from pathlib import Path

# Expected table schemas for validation
TABLE_SCHEMAS = {
    "cyber_incidents": ["incident_id", "timestamp", "severity", "category", "status", "description"],
    "it_tickets": ["ticket_id", "priority", "description", "status", "assigned_to", "created_at", "resolution_time_hours"],
    "datasets_metadata": ["dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"]
}


def validate_csv_schema(df, table_name):
    """Validate CSV columns match expected table schema (case-insensitive).
    Allows extra columns but requires all expected columns to be present."""
    if table_name not in TABLE_SCHEMAS:
        return True, None
    
    expected_cols = {col.lower() for col in TABLE_SCHEMAS[table_name]}
    actual_cols = {col.lower() for col in df.columns}
    
    missing = expected_cols - actual_cols
    
    if missing:
        missing_display = [col for col in TABLE_SCHEMAS[table_name] if col.lower() in missing]
        return False, f"Missing required columns: {', '.join(missing_display)}. Required columns: {', '.join(TABLE_SCHEMAS[table_name])}"
    
    # Extra columns are allowed and will be ignored
    return True, None


def load_csv_to_table(csv_path, table_name, if_exists="append"):
    """Load a CSV into a database table with schema validation."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")
    
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Validate schema before attempting insert
    is_valid, error_msg = validate_csv_schema(df, table_name)
    if not is_valid:
        raise ValueError(f"Schema validation failed: {error_msg}")

    # Select only the expected columns (case-insensitive matching)
    if table_name in TABLE_SCHEMAS:
        expected_cols = TABLE_SCHEMAS[table_name]
        # Create a mapping from actual column names (case-insensitive) to expected names
        col_mapping = {}
        df_cols_lower = {col.lower(): col for col in df.columns}
        
        for expected_col in expected_cols:
            if expected_col.lower() in df_cols_lower:
                actual_col_name = df_cols_lower[expected_col.lower()]
                col_mapping[actual_col_name] = expected_col
        
        # Select only the columns that match expected schema and rename them
        selected_cols = list(col_mapping.keys())
        df_filtered = df[selected_cols].rename(columns=col_mapping)
    else:
        df_filtered = df

    try:
        conn = connect_database()
        df_filtered.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=False
        )
        rows = len(df_filtered)
        conn.close()
        return rows
    except Exception as e:
        conn.close()
        raise ValueError(f"Failed to insert data into database: {e}")


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
