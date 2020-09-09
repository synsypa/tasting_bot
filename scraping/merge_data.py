import csv
import os
import pandas as pd
from datetime import datetime

csvs = os.listdir('scraped_data')
col_ref = {0:'producer',
           1:'name',
           2:'vintage',
           3:'score',
           4:'price_usd',
           5:'taster',
           6:'tasting_note',
           7:'n_produced',
           8:'n_imported'}

# Iterate over scraped files
out = []
for csvname in csvs:
    with open(f"scraped_data/{csvname}", 'r') as f:
        notes = csv.reader(f)
        for row in notes:
            # row[2] = row[2].replace('NV', '') # Recode NV to Blank
            row[4] = row[4].replace('$', '') # Remove Dollar Sign
            row[6] = row[6].strip()
            out.append(row)

# Create csv of cleaned files         
with open(f"processed_data/ws_merged_{datetime.utcnow().strftime('%Y%m%d')}.csv", "w") as m:
    writer = csv.writer(m)
    writer.writerow(col_ref.values())
    writer.writerows(out)