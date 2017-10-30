import csv
import pickle

# function to create trigram and bigram
def gen_trigram(words):
    if len(words) < 3:
        return
    for i in range(len(words) - 2):
        yield (words[i], words[i+1], words[i+2])

def gen_bigram(words):
    if len(words) < 2:
        return
    for i in range(len(words) - 1):
        yield (words[i], words[i+1])

# Load Merged Notes into list
noteslist = []
with open('ws_notes_2017-10-23_merged.csv', 'r') as f:
    notes = csv.reader(f)
    for row in notes:
        noteslist.append(row)
        
# Remove empty notes
noteslist = [['STARTSTART BEGINBEGIN ' + x[0] + ' ENDEND'] for x in noteslist if len(x) > 0]

# Create dictionary of bigrams to next word for notes
mc_dict = {}
for i in noteslist:
    words = i[0].split()
    for word1, word2, word3 in gen_trigram(words):
        key = (word1, word2)
        if key in mc_dict:
            mc_dict[key].append(word3)
        else:
            mc_dict[key] = [word3]

# Save to pkl
pickle.dump(mc_dict, open('basic_dict.pkl', 'wb'))

# Load Merged Names into list
nameslist = []
with open('ws_names_2017-10-23_merged.csv', 'r') as f:
    names = csv.reader(f)
    for row in names:
        nameslist.append(row)

# Remove empty notes
nameslist = [['STARTSTART ' + x[0] + ' ENDEND'] for x in nameslist if len(x) > 0]


# Create dictionary of bigrams to next word for notes
nm_dict = {}
for i in nameslist:
    words = i[0].split()
    for word1, word2 in gen_bigram(words):
        key = word1
        if key in nm_dict:
            nm_dict[key].append(word2)
        else:
            nm_dict[key] = [word2]

# Save to pkl       
pickle.dump(nm_dict, open('basic_name_dict.pkl', 'wb'))