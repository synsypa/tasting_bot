import csv
import os 
from datetime import datetime


csvs = os.listdir('scraped_data')

# Iterate over scraped files
merged = []
names = []
for csvname in csvs:
    with open(f"scraped_data/{csvname}", 'r') as f:
        notes = csv.reader(f)
        for row in notes:
            merged.append([row[6]])
            combined_name = ' '.join(row[0:3])
            names.append([combined_name])

# Create csv of notes         
with open(
        f"processed_data/ws_notes_merged_{datetime.utcnow().strftime('%Y%m%d')}.csv",
         "w") as m:
    writer = csv.writer(m)
    writer.writerow(merged)

# Create csv of names
with open(f"processed_data/ws_names_merged_{datetime.utcnow().strftime('%Y%m%d')}.csv",
         "w") as n:
    writer = csv.writer(n)
    writer.writerows(names)