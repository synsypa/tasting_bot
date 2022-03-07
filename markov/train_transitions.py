import csv
import pickle
from collections import defaultdict

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


if __name__ == "__main__":
    # Load Merged Notes into list
    with open('notes_merged.csv', 'r') as f:
        notes = f.read().split('\n')
            
    # Create dictionary of bigrams to next word for notes
    mc_dict = defaultdict(list)
    for i in notes:
        words = i.split()
        for word1, word2, word3 in gen_trigram(words):
            key = (word1, word2)
            mc_dict[key].append(word3)

    # Save to pkl
    pickle.dump(mc_dict, open('../bot/basic_note_dict.pkl', 'wb'))

    # Load Merged Names into list
    with open('names_merged.csv', 'r') as f:
        names = f.read().split('\n')

    # Create dictionary of bigrams to next word for notes
    nm_dict = defaultdict(list)
    for i in names:
        words = i.split()
        for word1, word2 in gen_bigram(words):
            nm_dict[word1].append(word2)

    # Save to pkl       
    pickle.dump(nm_dict, open('../bot/basic_name_dict.pkl', 'wb'))
