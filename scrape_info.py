from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
import requests as requests

import pandas as pd



# Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# # URL with filter for motorboats and ascending price sortation
# url = "https://www.boot24.ch/chde/occasionsboote/?cat=2&page=0&sort=chfasc"

# driver.get(url)

# # Wait for JavaScript to load
# time.sleep(5)

# # Get source HTML
# page = driver.page_source
# page = requests.get(url)

# soup = BeautifulSoup(page.text, 'html.parser')
# print(soup.prettify())

# # Get all hyperlinks in html
# a_objects = soup.find_all('a')

# # Make a list with all links that include 'details', those are single boat listings
# hyper_links = [item.get('href') for item in a_objects if 'detail' in item.get('href')]

# for link in hyper_links:
#     print(link)
# #print(hyper_links)



def get_listing_urls(boat_cat):
    
    n_page = 0

    # set page url
    #url = f'https://www.boot24.ch/chde/occasionsboote/?src=&cat={boat_cat}&whr=CHF&prs_min=&prs_max=&lge_min=&lge_max=&bre_min=&bre_max=&mah_min=&mah_max=&jhr_min=&jhr_max=&zus=&sort=chfasc'
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


df_links_motorboat = pd.DataFrame()
df_links_motorboat['links'] = get_listing_urls(2)


df_links_motorboat.to_csv('listings_motorboats.csv')