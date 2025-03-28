from datetime import datetime
import pandas as pd
import argparse
import os
from pipeline.stages.data_cleaning import DataCleaner

def main():

    date_stamp = datetime.today().strftime('%Y-%m-%d')
    # Bestehende Raw CSV einbinden
    try:
        raw_data = pd.read_csv("outputs/2025-03-28_raw_data.csv")
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")
        return

    # Step 5: Clean Data
    print("Cleaning data...")
    cleaner = DataCleaner()
    cleaned_data = cleaner.run(raw_data)

    # Step 6: Export Cleaned Datset
    cleaned_data.to_csv(f"outputs/{date_stamp}_cleaned_data.csv", index=False)
    print("=== Pipeline completed successfully ===")
if __name__ == "__main__":
    main()
