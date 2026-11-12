"""Load step: save the clean table into a SQLite database."""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "heart.db"
TABLE_NAME = "respondents"


def load(df, db_path=DB_PATH, table_name=TABLE_NAME):
    """Write the DataFrame to a SQLite table, replacing any old copy."""
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    return db_path


def count_rows(db_path=DB_PATH, table_name=TABLE_NAME):
    """Ask the database how many rows the table holds."""
    with sqlite3.connect(db_path) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]


if __name__ == "__main__":
    from transform import transform
    from extract import extract

    clean = transform(extract())
    path = load(clean)
    print(f"Saved to: {path}")
    print(f"Rows in database: {count_rows():,}")
    print(f"Rows in DataFrame: {len(clean):,}")