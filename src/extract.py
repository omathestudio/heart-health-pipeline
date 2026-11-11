""""Extract step: read the raw CDC BRFSS file into a pandas DataFrame."""

from pathlib import Path

import pandas as pd

# The project root is one level up from this file (src/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def find_raw_file():
    """Return the path to the BRFSS .XPT file in the data folder."""
    matches = list(DATA_DIR.glob("*.XPT"))
    if not matches:
        raise FileNotFoundError(f"No .XPT file found in {DATA_DIR}")
    return matches[0]


def extract(columns=None, chunksize=50_000):
    """Read the BRFSS file in chunks, keeping only the columns we need.
    
    columns: list column names to keep. None keeps all of them.
    chunksize: number of reows read at a time, so the laptop doesn't run out of memory.
    """
    path = find_raw_file()
    reader = pd.read_sas(path, format="xport", encoding="latin-1", chunksize=chunksize)

    chunks = []
    for chunk in reader:
        if columns is not None:
            chunk = chunk[columns]
        chunks.append(chunk)

    return pd.concat(chunks, ignore_index=True)


if __name__ == "__main__":
    # Quick look: read just the first chunk so we can see what's inside
    path = find_raw_file()
    reader = pd.read_sas(path, format="xport", encoding="latin-1", chunksize=5)
    preview = next(reader)
    print(f"File: {path.name}")
    print(f"Number of columns: {preview.shape[1]}")
    print(preview.iloc[:, :10])