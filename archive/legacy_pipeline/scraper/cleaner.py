import pandas as pd
import re
from utils.helpers import extract_int_column, clean_unit_string

def clean_scraped_data(df):
    df_cleaned = df.copy()

    rename_map = {
        "Price": "spec_price_chf",
        "id": "spec_listing_id",
        "spec_Baujahr": "spec_year_built",
        "spec_Zustand": "spec_condition",
        "spec_Länge x Breite": "spec_length_width",
        "spec_Material": "spec_material",
        "spec_zugel. Personenzahl": "spec_max_person",
        "spec_Anz. Kabinen": "spec_cabins",
        "spec_Antrieb": "spec_drive_type",
        "spec_Motor": "spec_motor",
        "spec_Motorleistung": "spec_motor_power",
        "spec_Treibstoff": "spec_fuel_type",
        "spec_Motorstunden": "spec_engine_hours",
        "spec_Tiefgang": "spec_draft",
        "spec_Verdrängung": "spec_displacement",
        "spec_Anz. Kojen": "spec_berths",
        "spec_Anz. Nasszellen": "spec_bathrooms",
        "spec_Gewicht": "spec_weight",
        "spec_Schalenfarbe": "spec_hull_color",
        "spec_CE-Kennzeichnung": "spec_ce_certification",
        "spec_Baujahr Motor": "spec_engine_year",
        "spec_Rumpftyp": "spec_hull_type",
        "spec_Brückendurchfahrtshöhe": "spec_bridge_clearance",
        "spec_Trailer": "spec_trailer",
        "spec_Verhandlungsbasis": "spec_price_negotiable",
        "spec_inkl. MwSt., Neuboot auf Bestellung": "new",
        "equip_Navigationsbeleuchtung": "equip_nav_lights",
        "equip_Feuerlöscher": "equip_fire_extinguisher",
        "equip_Anker": "equip_anchor",
        "equip_Batterie": "equip_battery",
        "equip_Ganzpersenning": "equip_full_cover",
        "equip_Bug-Ankerwinde": "equip_bow_anchor_winch",
        "equip_Cockpit-Persenning": "equip_cockpit_cover",
        "equip_Badeleiter": "equip_bathing_ladder",
        "equip_Radio": "equip_radio",
        "equip_Bilgepumpe": "equip_bilge_pump",
        "equip_Bimini-Top": "equip_bimini_top",
        "equip_Kompass": "equip_compass",
        "equip_Landanschluss": "equip_shore_connection",
        "equip_Batterieladegerät": "equip_battery_charger",
        "equip_UKW-Funk": "equip_vhf_radio",
        "equip_Geschwindigkeitsmesser": "equip_speedometer",
        "equip_Feuerlösch-Anlage": "equip_fire_suppression",
        "equip_Winterpersenning": "equip_winter_cover",
        "equip_Kühlschrank": "equip_fridge",
        "equip_Unterwasseranstrich": "equip_underwater_coating",
        "equip_Fishfinder": "equip_fishfinder",
    }

    df_cleaned.rename(columns=rename_map, inplace=True)

    # Drop unwanted columns
    df_cleaned.drop(columns=[
        "spec_N.A.",
        "spec_inkl. MwSt.",
        "spec_Verhandlungsbasis, bei Einfuhr in die Schweiz fallen ev. Zoll- und Umrüstungskosten an",
        "equip_has_trailer",
        "spec_"
    ], inplace=True, errors="ignore")

    # --- Clean and convert spec_price_chf ---
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

    # --- Clean and convert spec_engine_hours to integer ---
    if "spec_engine_hours" in df_cleaned.columns:
        df_cleaned["spec_engine_hours"] = (
            df_cleaned["spec_engine_hours"]
            .astype(str)
            .str.replace("'", "", regex=False)
            .str.replace("h", "", case=False, regex=False)
            .str.strip()
        )
        df_cleaned["spec_engine_hours"] = pd.to_numeric(df_cleaned["spec_engine_hours"], errors="coerce").astype(
            "Int64")

    # Extract and convert numeric fields
    for col in ["spec_max_person", "spec_cabins", "spec_berths", "spec_bathrooms"]:
        extract_int_column(df_cleaned, col)

    # Clean unit fields
    if "spec_weight" in df_cleaned.columns:
        df_cleaned.rename(columns={"spec_weight": "spec_weight_kg"}, inplace=True)
        df_cleaned["spec_weight_kg"] = clean_unit_string(df_cleaned["spec_weight_kg"], "kg").astype("Int64")

    if "spec_displacement" in df_cleaned.columns:
        df_cleaned.rename(columns={"spec_displacement": "spec_displacement_kg"}, inplace=True)
        df_cleaned["spec_displacement_kg"] = clean_unit_string(df_cleaned["spec_displacement_kg"], "kg").astype("Int64")

    if "spec_draft" in df_cleaned.columns:
        df_cleaned.rename(columns={"spec_draft": "spec_draft_m"}, inplace=True)
        df_cleaned["spec_draft_m"] = clean_unit_string(df_cleaned["spec_draft_m"], "m").astype(float)

    if "spec_bridge_clearance" in df_cleaned.columns:
        df_cleaned.rename(columns={"spec_bridge_clearance": "spec_bridge_clearance_m"}, inplace=True)
        df_cleaned["spec_bridge_clearance_m"] = clean_unit_string(df_cleaned["spec_bridge_clearance_m"], "m").astype(float)

    # Convert years
    for year_col in ["spec_year_built", "spec_engine_year"]:
        if year_col in df_cleaned.columns:
            df_cleaned[year_col] = pd.to_numeric(df_cleaned[year_col], errors="coerce").fillna(0).astype(int)

    # Length and width
    if "spec_length_width" in df_cleaned.columns:
        dims = df_cleaned["spec_length_width"].str.extract(r"(?P<length>\d+\.?\d*)\s*m\s*x\s*(?P<width>\d+\.?\d*)\s*m")
        df_cleaned["spec_length_m"] = dims["length"].astype(float)
        df_cleaned["spec_width_m"] = dims["width"].astype(float)
        df_cleaned.drop(columns=["spec_length_width"], inplace=True)

    # --- Clean and split spec_motor_power into float PS and kW ---
    if "spec_motor_power" in df_cleaned.columns:
        power = df_cleaned["spec_motor_power"].str.extract(r"(\d+(?:\.\d+)?)\s*PS\s*/\s*(\d+(?:\.\d+)?)\s*kW")
        df_cleaned["spec_motor_ps"] = pd.to_numeric(power[0], errors="coerce").astype(float)
        df_cleaned["spec_motor_kw"] = pd.to_numeric(power[1], errors="coerce").astype(float)

    # Fuel type split
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

    # Convert booleans
    for col in df_cleaned.columns:
        if col.startswith("equip_") or col in ["spec_trailer", "spec_price_negotiable", "new"]:
            df_cleaned[col] = df_cleaned[col].notna()

    return df_cleaned