import re
import requests
from bs4 import BeautifulSoup

def get_listing_urls(boat_cat):
    n_page = 0
    url = f"https://www.boot24.ch/chde/occasionsboote/?cat={boat_cat}&page={n_page}&sort=chfasc"
    response = requests.get(url)

    if response.status_code == 200:
        soup_main = BeautifulSoup(response.text, 'html.parser')
        span_objects = soup_main.find_all('span')
        pagination_links = [
            item.get('data-link') for item in span_objects
            if item.get('data-link') is not None and f'?cat={boat_cat}&page=' in item.get('data-link')
        ]
        max_page = int(re.search(r"page=(\d+)", pagination_links[4]).group(1))
        print(max_page)

    hyper_links = []

    while n_page <= max_page:
        url = f"https://www.boot24.ch/chde/occasionsboote/?cat={boat_cat}&page={n_page}&sort=chfasc"
        response = requests.get(url)

        if response.status_code == 200:
            print(f'Fetching: {url}')
            soup_main = BeautifulSoup(response.text, 'html.parser')
            a_objects = soup_main.find_all('a')
            page_links = list(set(item.get('href') for item in a_objects if 'detail' in item.get('href')))
            hyper_links.extend(page_links)
        else:
            print(f'404 Error for: {url}')

        n_page += 20

    hyper_links = list(set(hyper_links))
    for link in hyper_links:
        print(link)

    print(f'Number of listings {len(hyper_links)}')
    return hyper_links
