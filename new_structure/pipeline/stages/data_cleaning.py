import pandas as pd
import re
from config.column_mappings import RENAME_MAP, UNWANTED_COLUMNS
from utils.helpers import extract_int_column, clean_unit_string

class DataCleaner:
    def clean(self, df):
        """Applies all cleaning steps to the raw DataFrame."""
        df_cleaned = df.copy()

        # 1. Rename columns and drop unwanted ones
        df_cleaned = df_cleaned.rename(columns=RENAME_MAP)
        df_cleaned = df_cleaned.drop(columns=UNWANTED_COLUMNS, errors="ignore")

        # drop all columns containing "MwSt." or "Zoll"
        df_cleaned = df_cleaned.loc[:, ~df_cleaned.columns.str.contains("MwSt")]
        df_cleaned = df_cleaned.loc[:, ~df_cleaned.columns.str.contains("Zoll")]

        # 2. Clean numeric fields (price, engine hours)
        if "spec_price_chf" in df_cleaned.columns:
            df_cleaned["spec_price_chf"] = (
                df_cleaned["spec_price_chf"]
                .astype(str)
                .str.replace("CHF", "", regex=False)
                .str.replace("'", "", regex=False)
                .str.replace(".-", "", regex=False)
                .str.strip()
            )
            df_cleaned["spec_price_chf"] = pd.to_numeric(df_cleaned["spec_price_chf"], errors="coerce").astype("Int64")

        if "spec_engine_hours" in df_cleaned.columns:
            df_cleaned["spec_engine_hours"] = (
                df_cleaned["spec_engine_hours"]
                .astype(str)
                .str.replace("'", "", regex=False)
                .str.replace("h", "", case=False, regex=False)
                .str.strip()
            )
            df_cleaned["spec_engine_hours"] = pd.to_numeric(df_cleaned["spec_engine_hours"], errors="coerce").astype("Int64")

        # 3. Extract integers from columns like max_person, cabins, etc.
        for col in ["spec_max_person", "spec_cabins", "spec_berths", "spec_bathrooms", "spec_toilet", "spec_shower"]:
            if col in df_cleaned.columns:
                extract_int_column(df_cleaned, col)

        # 4. Clean unit-based columns (weight, displacement, draft)
        unit_columns = [
            ("spec_weight", "spec_weight_kg", "kg"),
            ("spec_displacement", "spec_displacement_kg", "kg"),
            ("spec_draft", "spec_draft_m", "m"),
            ("spec_bridge_clearance", "spec_bridge_clearance_m", "m"),
        ]

        for old_col, new_col, unit in unit_columns:
            if old_col in df_cleaned.columns:
                df_cleaned[new_col] = clean_unit_string(df_cleaned[old_col], unit)
                df_cleaned = df_cleaned.drop(columns=[old_col])
                if unit == "kg":
                    df_cleaned[new_col] = pd.to_numeric(df_cleaned[new_col], errors="coerce").astype("Int64")
                else:
                    df_cleaned[new_col] = pd.to_numeric(df_cleaned[new_col], errors="coerce").astype(float)

        # 5. Split length x width into separate columns
        if "spec_length_width" in df_cleaned.columns:
            dims = df_cleaned["spec_length_width"].str.extract(r"(?P<length>\d+\.?\d*)\s*m\s*x\s*(?P<width>\d+\.?\d*)\s*m")
            df_cleaned["spec_length_m"] = dims["length"].astype(float)
            df_cleaned["spec_width_m"] = dims["width"].astype(float)
            df_cleaned = df_cleaned.drop(columns=["spec_length_width"])

        # 6. Split motor power into PS/kW
        if "spec_motor_power" in df_cleaned.columns:
            power = df_cleaned["spec_motor_power"].str.extract(r"(\d+(?:\.\d+)?)\s*PS\s*/\s*(\d+(?:\.\d+)?)\s*kW")
            df_cleaned["spec_motor_ps"] = pd.to_numeric(power[0], errors="coerce").astype(float)
            df_cleaned["spec_motor_kw"] = pd.to_numeric(power[1], errors="coerce").astype(float)
            df_cleaned = df_cleaned.drop(columns=["spec_motor_power"])

        # 7. Split fuel type into tank size and fuel type
        if "spec_fuel_type" in df_cleaned.columns:
            def split_fuel_type(val):
                if pd.isna(val): return None, None
                match = re.match(r"(?:(\d+)\s*l)?\s*(.*)", val.strip(), re.IGNORECASE)
                if match:
                    tank = match.group(1)
                    fuel = match.group(2).strip()
                    return int(tank) if tank else None, fuel if fuel else ""
                return None, val

            tank_fuel = df_cleaned["spec_fuel_type"].apply(lambda x: split_fuel_type(x))
            df_cleaned["spec_tank_size"] = tank_fuel.apply(lambda x: x[0])
            df_cleaned["spec_fuel_type"] = tank_fuel.apply(lambda x: x[1])

        # 7a. Format water and waste tank sizes
        def extract_tank_size(val):
            if pd.isna(val): return None
            match = re.match(r"(\d+)\s*l", str(val).strip(), re.IGNORECASE)
            return int(match.group(1)) if match else None

        for col in ["spec_water_tank_l", "spec_waste_tank_l"]:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].apply(extract_tank_size)


        # 8. Convert boolean columns (equipment, trailer, etc.)
        boolean_cols = [col for col in df_cleaned.columns if col.startswith("equip_")] + ["spec_trailer", "spec_price_negotiable", "new"]
        for col in boolean_cols:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].notna()

        # 9. Clean year columns
        for year_col in ["spec_year_built", "spec_engine_year"]:
            if year_col in df_cleaned.columns:
                df_cleaned[year_col] = pd.to_numeric(df_cleaned[year_col], errors="coerce").astype("Int64")

        # 10. Clean empty price columns
        df_cleaned = df_cleaned.dropna(subset=['spec_price_chf'])

        return df_cleaned

    def run(self, df):
        """Entry point for the cleaning stage."""
        return self.clean(df)