# This file scrapes and processes the "Daily Picks" tasting notes and scores
# from winespectator.com saves them to a .csv 
# Last Run: 2020/07/12

from bs4 import BeautifulSoup
import requests
import re
import csv
import time
import random
import argparse
from logzero import logger
import logzero

PAGEDICT = {1:1112,
            2:1102,
            3:1089}


def split_note(note):

    # Separate Note and Taster
    split = note.split('—')
    text = split[0]
    if len(split) > 1:
        taster = split[1].strip()
        logger.debug(f"Extracted taster: {taster}")
    else:
        taster = None
        logger.debug("No Taster Found")

    # Extract N Made
    re_made = re.search(r'(\d+,?\d+) cases made[,.]?', text)
    if re_made:
        n_made = int(re_made.group(1).replace(',', ''))
        logger.debug(f"Extracted N Bottles Made: {n_made}")
        text = text.replace(re_made.group(0), '')
    else: 
        n_made = None
        logger.debug(f"No N Bottles Made Found")

    # Extract N Imported
    re_import = re.search(r'(\d+,?\d+) cases imported[,.]?', text)
    if re_import:
        n_import = int(re_import.group(1).replace(',', ''))
        logger.debug(f"Extracted N Bottles Imported: {n_import}")
        text = text.replace(re_import.group(0), '')
    else: 
        n_import = None
        logger.debug(f"No N Bottles Imported Found")
    
    return text, taster, n_made, n_import
    

def process_entry(wine_entry):
    # Extract Name
    name = wine_entry.find('h3').get_text().strip()
    logger.debug(f"Extracted name: {name}")

    # Extract Type and Vintage
    wtype_yr = wine_entry.find('h4').get_text().strip()
    if wtype_yr[-4:].isdigit():
        wtype = wtype_yr[:-4].strip()
        vintage = wtype_yr[-4:]
        logger.debug(f"Extracted vintage {vintage}")
    elif wtype_yr[-2:].isdigit():
        wtype = wtype_yr[:-2].strip()
        vintage = wtype_yr[-2:]
        if int(vintage) <= 25: #TKTK: do this check properly
            vintage = '20' + vintage
        else:
            vintage = '19' + vintage
        logger.debug(f"2 digit vintage found, using {vintage}")
    elif (wtype_yr[-2:] == 'NV') or ():
        wtype = wtype_yr[:-2].strip()
        vintage = 'NV'
        logger.debug(f"Vintage defined as Non-Vintage")
    else:
        wtype = wtype_yr
        vintage = None
        logger.debug(f"No vintage found")

    # Extract Score
    score = wine_entry.find('span', {'class': 'pwl-score'}).get_text()
    logger.debug(f"Extracted score: {score}")

    # Extract Price and Note
    price_note = wine_entry.find_all('p')
    price = price_note[0].get_text().strip()
    logger.debug(f"Extracted Price: {price}")
    note = price_note[1].get_text().strip()
    logger.debug(f"Extracted Note: {note}")

    text, taster, n_made, n_import = split_note(note)

    return [name,
            wtype,
            vintage,
            score,
            price,
            taster,
            text,
            n_made,
            n_import]

def scrape_single_page(category, page):
    
    url = f"https://www.winespectator.com/dailypicks/category/catid/{category}/page/{page}"
    processed_page = []

    logger.info(f"Attempting to retrieve {url}")
    response = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    if response.status_code != 200:
        logger.error(f"{url} returned code {response.status_code}")
    else:
        logger.info(f"{url} retrieved...")

    logger.info(f"Parsing page source...")
    soup = BeautifulSoup(response.text, "lxml")
    wines = soup.find_all("div", {"class": "d-flex"})

    if len(wines) == 0:
        logger.error(f"No wines found on {url}...")
        
    # Process each Page
    for w in wines:
        logger.info(f"Processing wine note entry...")
        processed_wine = process_entry(w)
        processed_page.append(processed_wine)

    return processed_page

def scrape_category(category):
    processed_cat = []
    for page in range(1, PAGEDICT[category]+1):
        processed_cat += scrape_single_page(category, page)
        # Sleep for random time betwen 5-10 seconds
        time.sleep(5 + random.randint(0,5))

    return processed_cat

def save_output(output, filename): 
    # Save result to .CSV
    logger.info(f"Saving output to raw_data/{filename}")
    with open(f"./scraped/{filename}.csv") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    return 1

def main(opts):
    logger.info(f"Starting Wine Spectator Scrape...")
    if not opts.category:
        for cat in range(1,4):
            logger.info(f"Scraping all pages of category {cat}...")
            category_wines = scrape_category(cat)
            save_output(category_wines, f'ws_cat{cat}')
    else:
        cat = int(opts.category)
        logger.info(f"Scraping all pages of category {cat}...")
        category_wines = scrape_category(cat)
        save_output(category_wines, f'ws_cat{cat}')
    return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", action="store")
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()

    if not args.debug:
        # Set minimum level of logger to info
        logzero.loglevel(level=20)

    main(args)


