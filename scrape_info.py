import re
from bs4 import BeautifulSoup
import requests as requests
from datetime import datetime
import pandas as pd


def get_listing_urls(boat_cat):
    """
    get_listing_urls scrapes through the marketplace of https://www.boot24.ch/chde/ for boats that are sold
    and retrieves every url that leads to the more detailed description of each boat listing

    :param boat_cat (int), defines the boat categories is scraped (1: sailboats, 2: motorboats)
    
    :return: list with all urls of every boat listing within category
    """ 
    
    n_page = 0

    # set page url
    url = f"https://www.boot24.ch/chde/occasionsboote/?cat={boat_cat}&page={n_page}&sort=chfasc"

    # Get source HTML of page
    response = requests.get(url)


    # get maximum page
    if response.status_code == 200:

        soup_main = BeautifulSoup(response.text, 'html.parser')
        #print(soup.prettify())

        # Get highest page number
        span_objects = soup_main.find_all('span')
        #print(span_objects)

        # Get highest number of pagination
        pagination_links = [item.get('data-link') for item in span_objects if item.get('data-link') is not None and'https://www.boot24.ch/chde/occasionsboote/?cat=2&page=' in item.get('data-link')]
        # print(pagination)

        # As long as the webpage structure is not changed it will always be the fifth object in the list
        # So we can just extract the highest page using regex
        max_page = int(re.search(r"page=(\d+)", pagination_links[4]).group(1))
        print(max_page)

    # list to store final hyperlinks
    hyper_links = []

    # iteratively extract all listing hyperlinks from pages up to the max page
    while n_page <= max_page:

        # set page url
        url = f"https://www.boot24.ch/chde/occasionsboote/?cat={boat_cat}&page={n_page}&sort=chfasc"

        # Get source HTML of page
        response = requests.get(url)

        if response.status_code == 200:
            
            print(f'Fetching: {url}')

            soup_main = BeautifulSoup(response.text, 'html.parser')
            #print(soup.prettify())
            
            # Get all hyperlinks of first page source HMTL
            a_objects = soup_main.find_all('a')

            # Make a list with all links that include 'detail', those are single boat listings
            page_links = [item.get('href') for item in a_objects if 'detail' in item.get('href')]
            page_links = list(set(page_links)) # get unique values
            
            # append to list of hyperlinks
            hyper_links.extend(page_links)
        else:
             print(f'404 Error for: {url}')
        

        # Increment page, akways +20 this logic is from webpage
        n_page += 20

        # # for debugging
        # if n_page >= 200:
        #     break
    


    # The final list should again be only unique values
    hyper_links = list(set(hyper_links))

    for link in hyper_links:
            print(link)

    print(f'Number of listings {len(hyper_links)}')

    return hyper_links


def scrape_listings(listings):
    """
    scrape_listings takes a list of links for boat listings as an input and scrapes each
    boat listing seperately for information (price, specifications, equipment)

    :param listings: list that contains url's for boat listings on https://www.boot24.ch/chde/
    
    :return: pandas dataframe where each listing represents a row and columns represent either represent general information
    like price, name of the boat, other specifications (prefix: spec) or of some type of equipment is available on the boat (prefix: equip)
    """ 
    print(f'Number of listings: {len(listings)}')

    df_scraped_listings = pd.DataFrame()

    # iteratively scrape single listings and put info into dataframe
    for url in listings:
        
        # Request single listing
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Listing with url {url} not found')
            pass
        
        # Extract Listing ID from url
        print(f'Scraping: {url}')
        match = re.search(r'/(\d+)/$', url)
        if match:
            id = match.group(1)
        else:
            id = None

        # Scrape Information from Listing 
        soup_listing = BeautifulSoup(response.text, 'html.parser')
        #print(soup_listing.prettify())
        specs_div = soup_listing.find('div', id='specs')
        #print(specs_div.prettify())

        # Extract Price
        price = "N.A."
        aside_section = soup_listing.find('aside')
        if aside_section:
            price_tag = aside_section.find('p', class_='contact-box__price')
            if price_tag:
                strong_tag = price_tag.find('strong')
                if strong_tag:
                    price = strong_tag.text.strip()

        #print(price)

        # Extract Specifications
        specs = {}
        specs_div = soup_listing.find('div', id='specs')
        if specs_div:
            for spec in specs_div.find_all('li'):
                key_span = spec.find('span', class_='list__key')
                value_span = spec.find('span', class_='list__value')
                category = key_span.text.strip() if key_span else "N.A."
                category = f'spec_{category}'
                value = value_span.text.strip() if value_span else "N.A."
                specs[category] = value

        #print(specs)

        # Extract Equipment
        equipment = {}
        equipment_div = soup_listing.find('div', id='equipment')
        if equipment_div:
            for item in equipment_div.find_all('li'):
                equipment_name = f'equip_{item.text.strip()}'
                if equipment_name:
                    equipment[equipment_name] = True
        
        #print(equipment)
        
        dict_listing = {
            'URL': url,
            'Price': price,
            'id' : id,
            **specs,
            **{key: equipment.get(key, False) for key in equipment}
        }

        #print(dict_listing)

        # Make dataframe from listing
        df_listing = pd.DataFrame.from_dict([dict_listing])
        #print(df_listing)

        # Add to big dataframe
        df_scraped_listings = pd.concat([df_scraped_listings, df_listing])
    
    print(f'Number of scraped listings: {len(df_scraped_listings)}')

    return df_scraped_listings


def main():

    # Create Datestamp
    date_stamp = datetime.today().strftime('%Y-%m-%d')

    # Retrieve all links for Motorboats listings (cat=2)
    list_motorboats = get_listing_urls(2)

    # save to csv
    df_links_motorboats = pd.DataFrame()
    df_links_motorboats['links'] = get_listing_urls(2)
    df_links_motorboats.to_csv(f'{date_stamp}_listings_motorboats.csv')

    # scrape information and save to csv
    df_motorboats_scraped = scrape_listings(list_motorboats)
    df_motorboats_scraped.to_csv(f'{date_stamp}_scraped_listings.csv')

    print(df_motorboats_scraped.head(10))
    

# run main
if __name__ == "__main__":
    main()