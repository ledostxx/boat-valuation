import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_listings(links_df):
    print(f'Number of listings to scrape: {len(links_df)}')
    df_scraped_listings = pd.DataFrame()

    for new_id, row in links_df.iterrows():
        url = row['links']
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Listing with url {url} not found')
            continue

        print(f'Scraping: {url}')
        match = re.search(r'/(\d+)/$', url)
        listing_id = match.group(1) if match else None

        soup_listing = BeautifulSoup(response.text, 'html.parser')

        price = "N.A."
        aside_section = soup_listing.find('aside')
        if aside_section:
            price_tag = aside_section.find('p', class_='contact-box__price')
            if price_tag and price_tag.find('strong'):
                price = price_tag.find('strong').text.strip()

        specs = {}
        specs_div = soup_listing.find('div', id='specs')
        if specs_div:
            for spec in specs_div.find_all('li'):
                key = spec.find('span', class_='list__key')
                value = spec.find('span', class_='list__value')
                specs[f"spec_{key.text.strip() if key else 'N.A.'}"] = value.text.strip() if value else "N.A."

        equipment = {}
        equipment_div = soup_listing.find('div', id='equipment')
        if equipment_div:
            for item in equipment_div.find_all('li'):
                equipment[f"equip_{item.text.strip()}"] = True

        dict_listing = {
            'new_id': new_id,
            'URL': url,
            'Price': price,
            'id': listing_id,
            **specs,
            **{key: equipment.get(key, False) for key in equipment}
        }

        df_listing = pd.DataFrame.from_dict([dict_listing])
        df_scraped_listings = pd.concat([df_scraped_listings, df_listing], ignore_index=True)

    df_scraped_listings.set_index('new_id', inplace=True)
    print(f'Number of scraped listings: {len(df_scraped_listings)}')
    return df_scraped_listings