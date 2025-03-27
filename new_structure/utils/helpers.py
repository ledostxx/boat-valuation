import pandas as pd


def extract_int_column(df, col):
    """
    Extracts the first integer from a string column and converts it to an integer.

    Args:
        df (pd.DataFrame): DataFrame containing the column.
        col (str): Name of the column to process.
    """
    if col in df.columns:
        # Extract the first sequence of digits
        df[col] = df[col].str.extract(r"(\d+)")
        # Convert to numeric, handle errors, and cast to integer
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)


def clean_unit_string(series, unit):
    """
    Cleans a pandas Series by removing a specified unit and other non-numeric characters.

    Args:
        series (pd.Series): The Series to clean (e.g., "1'200 kg" → "1200").
        unit (str): The unit to remove (e.g., "kg", "m").

    Returns:
        pd.Series: Cleaned Series with stripped units and characters.
    """
    return (
        series.astype(str)
        .str.replace(unit, "", case=False, regex=False)  # Remove unit (case-insensitive)
        .str.replace("'", "", regex=False)  # Remove apostrophes (e.g., 1'200 → 1200)
        .str.strip()  # Remove leading/trailing whitespace
    )