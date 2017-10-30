import csv

csvs = ['winespectator_2017-10-23_1.csv',
        'winespectator_2017-10-23_2.csv',
        'winespectator_2017-10-23_3.csv']

# Iterate over scraped files
merged = []
names = []
for csvname in csvs:
    with open(csvname, 'r') as f:
        notes = csv.reader(f)
        for row in notes:
            merged.append([row[6]])
            names.append([row[0]])

# Create csv of notes         
with open("ws_notes_2017-10-23_merged.csv", "w") as m:
    writer = csv.writer(m)
    writer.writerow(merged)

# Create csv of names
with open("ws_names_2017-10-23_merged.csv", "w") as n:
    writer = csv.writer(n)
    writer.writerows(names)