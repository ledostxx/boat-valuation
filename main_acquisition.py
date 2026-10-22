from datetime import datetime
import pandas as pd
import argparse
import os
from pipeline.stages.data_acquisition import DataAcquisition
from pipeline.stages.data_cleaning import DataCleaner

def main():

    date_stamp = datetime.today().strftime('%Y-%m-%d')
    # Bestehende Raw CSV einbinden
    try:
        urls_df = pd.read_csv("outputs/2025-04-04_urls.csv")
        urls = urls_df['links'].tolist()
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")
        return


    # Initialize DataAcquisition (boat_category might not be needed if using existing URLs)
    acquirer = DataAcquisition(boat_category=2)

    # Step 3: Scrape Details
    print("Scraping listing details...")
    raw_data = acquirer.scrape_listing_details(urls)
    print(f"Scraped {len(raw_data)} listings")

    # Step 4: Export Raw Dataset
    raw_data.to_csv(f"outputs/{date_stamp}_raw_data.csv", index=False)
    print(f"Raw data saved to outputs/{date_stamp}_raw_data.csv")

    # Step 5: Clean Data
    print("Cleaning data...")
    cleaner = DataCleaner()
    cleaned_data = cleaner.run(raw_data)

    # Step 6: Export Cleaned Dataset
    cleaned_data.to_csv(f"outputs/{date_stamp}_cleaned_data.csv", index=False)
    print("=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main()