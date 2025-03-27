from datetime import datetime
import pandas as pd
from pipeline.stages.data_acquisition import DataAcquisition
from pipeline.stages.data_cleaning import DataCleaner


def main():
    print("=== Starting pipeline ===")

    # Step 1: Data Acquisition
    print("Fetching listing URLs...")
    acquirer = DataAcquisition(boat_category=2)
    urls = acquirer.get_listing_urls()
    print(f"Found {len(urls)} URLs")

    # Step 2: Scrape Details
    print("Scraping listing details...")
    raw_data = acquirer.scrape_listing_details(urls)
    print(f"Scraped {len(raw_data)} listings")

    # Step 3: Clean Data
    print("Cleaning data...")
    cleaner = DataCleaner()
    cleaned_data = cleaner.run(raw_data)

    # Export
    date_stamp = datetime.today().strftime('%Y-%m-%d')
    cleaned_data.to_csv(f"outputs/{date_stamp}_cleaned_data.csv", index=False)
    print("=== Pipeline completed successfully ===")


if __name__ == "__main__":
    main()