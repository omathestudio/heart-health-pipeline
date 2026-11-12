"""Extract step: read the raw CDC BRFSS file into a pandas DataFrame."""

from pathlib import Path

import pandas as pd

# The project root is one level up from this file (src/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# Columns we keep from the 283 in the raw file (see the 2025 BRFSS codebook)
HEART_COLUMNS = [
    # Outcome
    "_MICHD", "CVDINFR4", "CVDCRHD4", "CVDSTRK3",
    # Demographics
    "_STATE", "_SEX", "_AGEG5YR", "_EDUCAG", "_INCOMG1",
    # Risk factors
    "_RFHYPE6", "_RFCHOL3", "DIABETE4", "_BMI5", "_SMOKER3", "_TOTINDA", "_RFDRHV9", "GENHLTH",
    # Survey weight
    "_LLCPWT"
]


def find_raw_file():
    """Return the path to the BRFSS .XPT file in the data folder."""
    matches = list(DATA_DIR.glob("*.XPT"))
    if not matches:
        raise FileNotFoundError(f"No .XPT file found in {DATA_DIR}")
    return matches[0]


def extract(columns=HEART_COLUMNS, chunksize=50_000):
    """Read the BRFSS file in chunks, keeping only the columns we need.
    
    columns: list of column names to keep. None keeps all of them.
    chunksize: number of rows read at a time, so the laptop doesn't run out of memory.
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
    # Test run: read the full file and show the first few rows
    df = extract()
    print(f"Rows: {len(df):,} Columns: {df.shape[1]}")
    print(df.head())