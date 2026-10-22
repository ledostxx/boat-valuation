from datetime import datetime
import pandas as pd

from scraper.listings import get_listing_urls
from scraper.details import scrape_listings
from scraper.cleaner import clean_scraped_data

def main():
    date_stamp = datetime.today().strftime('%Y-%m-%d')

    list_motorboats = get_listing_urls(2)
    df_links_motorboats = pd.DataFrame({'links': list_motorboats})
    df_links_motorboats.index.name = "new_id"
    df_links_motorboats.to_csv(f'output/{date_stamp}_listings_motorboats.csv')

    df_motorboats_scraped = scrape_listings(df_links_motorboats)
    df_motorboats_scraped.index.name = "new_id"

    df_motorboats_cleaned = clean_scraped_data(df_motorboats_scraped)
    df_motorboats_cleaned.to_csv(f'output/{date_stamp}_scraped_listings.csv', encoding='utf-8')

    print(df_motorboats_cleaned.head(10))

if __name__ == "__main__":
    main()