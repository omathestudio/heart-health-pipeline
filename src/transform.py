"""Transform step: clean the raw BRFSS codes and turn them into readable data."""

import pandas as pd

# --- 1. Yes/no columns ---
# For each column: which raw code means "yes" and which means "no".
# Any other code (don't know, refused, missing) becomes a blank (NaN).

YES_NO_COLUMNS = {
    # raw name:   (new name,                yes, no)
    "_MICHD":     ("heart_disease",          1, 2),
    "CVDINFR4":   ("heart_attack",           1, 2),
    "CVDCRHD4":   ("coronary_hd",            1, 2),
    "CVDSTRK3":   ("stroke",                 1, 2),
    "_RFHYPE6":   ("high_bp",                2, 1),
    "_RFCHOL3":   ("high_cholesterol",       2, 1),
    "_TOTINDA":   ("inactive",               2, 1),  # 2 = no exercise in past 30 days
    "_RFDRHV9":   ("heavy_drinker",          2, 1),
}


# --- 2. Category columns ---
# Raw code -> readable label. Codes not listed (e.g. 9 = refused) become blank.

LABELS = {
    "_SEX": ("sex", {1: "Male", 2: "Female"}),
    "_AGEG5YR": ("age_group", {
        1: "18-24", 2: "25-29", 3: "30-34", 4: "35-39", 5: "40-44",
        6: "45-49", 7: "50-54", 8: "55-59", 9: "60-64", 10: "65-69",
        11: "70-74", 12: "75-79", 13: "80+",
    }),
    "_EDUCAG": ("education", {
        1: "No high school diploma", 2: "High school graduate",
        3: "Some college", 4: "College graduate",
    }),
    "_INCOMG1": ("income", {
        1: "Under $15k", 2: "$15k-$25k", 3: "$25k-$35k", 4: "$35k-$50k",
        5: "$50k-$100k", 6: "$100k-$200k", 7: "$200k+",
    }),
    "_SMOKER3": ("smoking_status", {
        1: "Current (every day)", 2: "Current (some days)",
        3: "Former", 4: "Never",
    }),
    "GENHLTH": ("general_health", {
        1: "Excellent", 2: "Very good", 3: "Good", 4: "Fair", 5: "Poor",
    }),
}


def make_yes_no(raw, yes_code, no_code):
    """Turn a raw yes/no column into 1 (yes, 0 (no) or blank."""
    return raw.map({yes_code: 1, no_code: 0}).astype("Int8")


def transform(raw_df):
    """Take the raw extract and return a clean, readable table."""
    df = pd.DataFrame(index=raw_df.index)

    # Yes/no columns -> 1 / 0 / blank
    for raw_name, (new_name, yes, no) in YES_NO_COLUMNS.items():
        df[new_name] = make_yes_no(raw_df[raw_name], yes, no)

    # Diabetes has extra answers, so it gets its own rule:
    # 1 = yes; 2 = only during pregnancy, 3 = no, 4 = pre-diabetes -> no
    df["diabetes"] = raw_df["DIABETE4"].map({1: 1, 2: 0, 3: 0, 4: 0}).astype("Int8")

    # Category columns -> readable labels
    for raw_name, (new_name, mapping) in LABELS.items():
        df[new_name] =  raw_df[raw_name].map(mapping)

    # BMI is stored without its decimal point: 2734 means 27.34
    df["bmi"] = raw_df["_BMI5"] / 100

    # Keep these as they are
    df["state_fips"] = raw_df["_STATE"].astype("Int16")
    df["survey_weight"] = raw_df["_LLCPWT"]

    return df


def weighted_rate(df, column):
    """Percentage of the population with column == 1, using the survey weight."""
    answered = df[column].notna()
    weights = df.loc[answered, "survey_weight"]
    yes = df.loc[answered, column]
    return 100 * (yes * weights).sum() / weights.sum()


if __name__ == "__main__":
    from extract import extract

    clean = transform(extract())

    print(f"Rows: {len(clean):,} Columns: {clean.shape[1]}")
    print("\nBlanks per column:")
    print(clean.isna().sum())
    print(f"\nHeart disease (weighted): {weighted_rate(clean, 'heart_disease'):.1f}%")
    print("\nFirst 5 rows:")
    print(clean.head())

