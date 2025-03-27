import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

class DataAcquisition:
    def __init__(self, boat_category=2):
        self.boat_category = boat_category
        self.base_url = "https://www.boot24.ch/chde/occasionsboote/"

    def get_listing_urls(self):
        """Fetch all listing URLs."""
        n_page = 0
        hyper_links = []

        # Get max page using the same logic as the initial code
        initial_url = f"{self.base_url}?cat={self.boat_category}&page={n_page}&sort=chfasc"
        response = requests.get(initial_url)
        max_page = 0

        if response.status_code == 200:
            soup_main = BeautifulSoup(response.text, 'html.parser')
            pagination_links = [
                item.get('data-link') for item in soup_main.find_all('span')
                if item.get('data-link') and f'?cat={self.boat_category}&page=' in item.get('data-link')
            ]
            if pagination_links and len(pagination_links) >= 5:
                max_page_match = re.search(r"page=(\d+)", pagination_links[4])
                if max_page_match:
                    max_page = int(max_page_match.group(1))
                    print(f"Determined max_page: {max_page}")
                else:
                    print("Failed to extract max_page from pagination_links[4].")
            else:
                print("Not enough pagination links found; defaulting max_page to 0.")
        else:
            print(f"Initial URL returned status code {response.status_code}")

        # Fetch all pages
        while n_page <= max_page:
            url = f"{self.base_url}?cat={self.boat_category}&page={n_page}&sort=chfasc"
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Fetching: {url}")
                soup_main = BeautifulSoup(response.text, 'html.parser')
                page_links = list(set(
                    item.get('href') for item in soup_main.find_all('a')
                    if 'detail' in item.get('href', '')
                ))
                hyper_links.extend(page_links)
            else:
                print(f"404 Error for: {url}")
            n_page += 20

        # Return the unique listing URLs
        urls = list(set(hyper_links))
        print(f"Total URLs found: {len(urls)}")
        return urls

    def scrape_listing_details(self, urls):
        """Scrape details from each URL and return a DataFrame."""
        print(f'Number of listings to scrape: {len(urls)}')
        data = []  # List to hold all scraped data as dictionaries

        for idx, url in enumerate(urls):
            print(f'Scraping {idx + 1}/{len(urls)}: {url}')
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Skipping {url} (HTTP {response.status_code})')
                continue

            # Extract listing ID from URL
            match = re.search(r'/(\d+)/$', url)
            listing_id = match.group(1) if match else None

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Price Extraction ---
            price = "N.A."
            aside = soup.find('aside')
            if aside:
                price_tag = aside.find('p', class_='contact-box__price')
                if price_tag and price_tag.find('strong'):
                    price = price_tag.find('strong').text.strip()

            # --- Specifications Extraction ---
            specs = {}
            specs_div = soup.find('div', id='specs')
            if specs_div:
                for item in specs_div.find_all('li'):
                    key_span = item.find('span', class_='list__key')
                    value_span = item.find('span', class_='list__value')

                    key = f"spec_{key_span.text.strip()}" if key_span else "spec_N.A."
                    value = value_span.text.strip() if value_span else "N.A."
                    specs[key] = value

            # --- Equipment Extraction ---
            equipment = {}
            equip_div = soup.find('div', id='equipment')
            if equip_div:
                for item in equip_div.find_all('li'):
                    equip_key = f"equip_{item.text.strip()}"
                    equipment[equip_key] = True

            # --- Combine Data ---
            listing_data = {
                'new_id': idx,  # Use index as temporary ID
                'URL': url,
                'Price': price,
                'id': listing_id,
                **specs,
                **equipment
            }

            data.append(listing_data)

        # Create DataFrame once (more efficient than repeated concat)
        df = pd.DataFrame(data)
        df.set_index('new_id', inplace=True)

        print(f'Successfully scraped {len(df)} listings')
        return df

    def run(self):
        urls = self.get_listing_urls()
        return self.scrape_listing_details(urls)