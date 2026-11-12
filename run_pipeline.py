"""Run the whole Heart Health Pipeline: extract -> transform -> load -> charts."""

import sys
import time
from pathlib import Path

# Let Python find the modules inside the src/ folder
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from extract import extract
from transform import transform, weighted_rate
from load import load, count_rows
from charts import make_all_charts


def step(name):
    """Print a step heading and return the start time."""
    print(f"\n[{name}]")
    return time.time()


def done(start):
    """Print how long a step took."""
    print(f"  done in {time.time() - start:.1f}s")


def main():
    pipeline_start = time.time()

    start = step("1/4 Extract: reading the raw BRFSS file")
    raw = extract()
    print(f"  {len(raw):,} rows, {raw.shape[1]} columns")
    done(start)

    start = step("2/4 Transform: cleaning codes and adding labels")
    clean = transform(raw)
    print(f"  Heart disease (weighted): {weighted_rate(clean, 'heart_disease'):.1f}%")
    done(start)

    start = step("3/4 Load: saving to the SQLite database")
    load(clean)
    rows_in_db = count_rows()
    print(f"  {rows_in_db:,} rows in database")
    if rows_in_db != len(clean):
        raise ValueError("Row count in database doesn't match the DataFrame")
    done(start)

    start = step("4/4 Charts: running SQL queries and saving charts")
    make_all_charts()
    done(start)

    print(f"\nPipeline finished in {time.time() - pipeline_start:.1f}s")


if __name__ == "__main__":
    main()