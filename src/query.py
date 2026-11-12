"""Query step: run the named SQL queries in sql/queries.sql against the database."""

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "sql" / "queries.sql"
DB_PATH = PROJECT_ROOT / "data" / "heart.db"


def read_queries(sql_file=SQL_FILE):
    """Split the .sql file into a dictionary of {query name: SQL text}."""
    queries = {}
    name = None
    for line in Path(sql_file).read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name:"):
            name = line.replace("-- name:", "").strip()
            queries[name] = ""
        elif name is not None:
            queries[name] += line + "\n"
    return queries


def run_query(name, db_path=DB_PATH, sql_file=SQL_FILE):
    """Run one named query and return the results as a DataFrame."""
    sql = read_queries(sql_file)[name]
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn)


if __name__ == "__main__":
    for name in read_queries():
        print(f"\n=== {name} ===")
        print(run_query(name).to_string(index=False))