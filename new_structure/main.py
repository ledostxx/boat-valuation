from datetime import datetime
import pandas as pd
from pipeline.stages.data_acquisition import DataAcquisition
from pipeline.stages.data_cleaning import DataCleaner


def main():
    date_stamp = datetime.today().strftime('%Y-%m-%d')
    print("=== Starting pipeline ===")

    # Step 1: Data Acquisition
    print("Fetching listing URLs...")
    acquirer = DataAcquisition(boat_category=2)
    urls = acquirer.get_listing_urls()

    # Step 2: Export URL List
    urls_prepare = pd.DataFrame()
    urls_prepare["links"] = urls
    urls_prepare.index.name = "new_id"
    urls_prepare.to_csv(f"outputs/{date_stamp}_urls.csv", index=True)
    print(f"Found {len(urls)} URLs")


    # Step 3: Scrape Details
    print("Scraping listing details...")
    raw_data = acquirer.scrape_listing_details(urls)
    print(f"Scraped {len(raw_data)} listings")

    # Step 4: Export Raw Datset
    raw_data.to_csv(f"outputs/{date_stamp}_raw_data.csv", index=False)
    print(f"Raw data saved to outputs/{date_stamp}_raw_data.csv")

    # Step 5: Clean Data
    print("Cleaning data...")
    cleaner = DataCleaner()
    cleaned_data = cleaner.run(raw_data)

    # Step 6: Export Cleaned Datset
    cleaned_data.to_csv(f"outputs/{date_stamp}_cleaned_data.csv", index=False)
    print("=== Pipeline completed successfully ===")


if __name__ == "__main__":
    main()