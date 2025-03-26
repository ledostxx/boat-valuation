import pandas as pd

def extract_int_column(df, col):
    if col in df.columns:
        df[col] = df[col].str.extract(r"(\d+)")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

def clean_unit_string(series, unit):
    return (
        series.str.replace(unit, "", case=False, regex=False)
              .str.replace("'", "", regex=False)
              .str.strip()
    )
