# CIP
Group work

Current Execution Flow:

1. main.py calls get_listing_urls (listings.py) to get all listing URLs for motorboats (category 2).

2. Saves these URLs to a CSV.

3. Passes the URLs to scrape_listings (details.py) to scrape each page's details.

4. The scraped data is cleaned using clean_scraped_data (cleaner.py) which renames, drops, converts, and processes columns.

5. The cleaned data is saved to another CSV.