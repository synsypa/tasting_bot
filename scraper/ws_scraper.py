# This file scrapes and processing Tasting notes from Wine Spectator Website
# processes basic wine attributes and saves them to a .csv 
# Last Run: 2017/10/23

from bs4 import BeautifulSoup
import re
import requests
import csv
import time
from random import randint
from logzero import logger

WS_CATS = ['less_than_15', '15_to_30', 'more_than_30']
PAGES = range(1,400)

# Scrape from Wine Spectator Daily Picks Page
template = "http://www.winespectator.com/dailypicks/{}/page/{}"
output = []
for cat in WS_CATS:
    for page in PAGES:
        site = template.format(cat, page)
        response = requests.get(site)
        logger.info(f"processing {response.url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = soup.find_all('div', {'class': 'd-flex'})
        
        # Process each Page
        for r in reviews:
            try:
                # Process Wine and Vintage
                wine_name = r.find('h4', {'class': 'mb-8'}).find('a', {'class': 'text-gray-darkest'}).get_text()
                if bool(re.search('\(\d\d\d\d\)$', wine_name)):
                    wine = re.sub('NV \(\d\d\d\d\)$', '', wine_name).strip()
                    vintage = 'NV'
                else:
                    wine = re.sub('\d\d\d\d\$', '', wine_name).strip()
                    vintage = re.search('(\d\d\d\d)$', wine_name).groups()[-1].strip()

                # Process Winemaker
                maker = r.find('h3', {'class': 'mb-8'}).find('a', {'class': 'text-gray-darkest'}).get_text()

                # Process Points and Price
                p_text = r.find_all('p')
                price_re = re.search("\$(\d\d*)", p_text[0].get_text())
                price = 'NA' if price_re is None else int(price_re.group(1))
                points = int(r.find('span', {'class':'pwl-score'}).get_text())

                # Process Note and Taster
                taster = re.sub(r'[^A-Za-z0-9 ]+', '', p_text[1].find('em').get_text()).strip()
                note =  p_text[1].get_text().split('\n')[1].strip()

                output.append([wine, maker, vintage, points, price, taster, note, cat])
                time.sleep(randint(0,3))
            except ValueError: 
                logger.error(f'problematic note on {response.url}')

        logger.info(f"{len(output)} notes processed after category {cat}, page {page}")

        # Save result to .CSV
        if page % 10 == 0:
            if len(output) > 0:
                logger.info(f"saving {cat} pages {page-9} to {page} to csv")
                with open(f"../corpora/ws_{cat}_{page-9}-{page}.csv", "w") as f:
                    writer = csv.writer(f, delimiter='\036')
                    writer.writerows(output)
                output = []

if len(output) > 0:
    logger.info(f"saving last {cat} notes to csv")
    with open(f"../corpora/ws_{cat}_{page}.csv", "w") as f:
        writer = csv.writer(f, delimiter='\036')
        writer.writerows(output)