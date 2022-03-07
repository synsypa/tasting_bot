# tasting_bot

This repo contains the code that backs the Twitter bot @SommMarkov, a Markov Chain generative text bot trained from WineSpectator Daily Picks tasting notes as well as English translations of Dream of the Red Chamber, The Analects of Confucius, and the Art of War (via Project Gutenberg).

* Markov transitions for notes are calculated based on Bigram -> Word transition probabilities and stored in `basic_note_dict.pkl`
* Markov transition for wine names and vintages are calculated as Word -> Word transition probablities and stored in `basic_name_dict.pkl`

## scraper
This repo also contains the code for a rudimentary scraper for Wine Spectator's DailyPicks notes.
