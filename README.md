# tasting_bot

This both tunes GPT2 to output wine tasting notes by using Wine Spectator Daily Pick tasting notes as training data. Output can be found on @SOMMarkov on twitter (twitter.com/SOMMarkov)

## Notes
Trained on Google Colab Notebook over 10 epochs

## Potential Expansions
* Better End to End capabilities (i.e. process scraped data in Dataset class)
* Recieve @s and reply with generated notes
* Scrap more sources of notes for better training set

Base dataset scraped from Wine Spectator review notes

Twitter integration based heavily on https://github.com/srome/markovbot
