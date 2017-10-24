# This file scrapes and processing Tasting notes from Wine Spectator Website
# processes basic wine attributes and saves them to a .csv 
# Last Run: 2017/10/23

from bs4 import BeautifulSoup
import regex
import requests
import csv
import time

# Scrape from Wine Spectator Daily Picks Page
template = "http://www.winespectator.com/dailypicks/category/catid/{}/page/{}"
output = []
for cat in range(1,4):
    for page in range(1,901):
        site = template.format(cat, page)
        response = requests.get(site)
        print(response.url)
        soup = BeautifulSoup(response.text, "lxml")
        lines = soup.find_all('h5')
        
        # Process each Page
        for l in lines[:-4]:
            # Process Wine, Vintage, and Maker
            wine_yr = l.find('a').get_text()
            if wine_yr[-2:] == 'NV':
                wine = wine_yr[:-2].strip()
                vintage = 'NV'
            else:
                wine = wine_yr[:-4].strip()
                vintage = wine_yr[-4:]
            maker = ' '.join(regex.findall('[\p{Lu}]{2,}',  wine))
            wine = regex.sub('[\p{Lu}]{2,}', '', wine).strip()

            # Process Points and Price
            pt_price = l.find('h6').get_text()
            pp_split = pt_price.split(',')
            points = pp_split[0].strip()
            price = pp_split[1].strip()

            # Process Note and Taster
            note_taster = l.find('div', attrs={'class':'paragraph'}).get_text().strip()
            nt_split = note_taster.split('—')
            note = nt_split[0].strip()
            taster = nt_split[1].strip()

            output.append([wine, maker, vintage, points, price, taster, note])
            time.sleep(10)

# Save result to .CSV
with open("winespectator_2017_10_23.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(output)
    