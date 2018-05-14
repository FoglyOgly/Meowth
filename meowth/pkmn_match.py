from fuzzywuzzy import fuzz
from fuzzywuzzy import process

WORDS = None

def set_list(word_list):
    global WORDS
    WORDS = word_list

def get_pkmn(word):
    result = process.extractOne(word, WORDS, scorer=fuzz.ratio, score_cutoff = 60)
    if result is None:
        index = None
    else:
        pkmn = result[0]
        index = WORDS.index(pkmn)
    return(index)
