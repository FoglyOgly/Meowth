# Sourced from
# http://norvig.com/spell-correct.html,
# with the English-language dictionary replaced by the Pokemon name list

import re
import json
from collections import Counter
import gettext

config = {}
with open("config.json","r") as fd:
    config = json.load(fd)

language = gettext.translation('meowth', localedir='locale', languages=[config['language']])
language.install()

pokemon_path_source = "locale/{0}/pkmn.json".format(config['language'])


with open(pokemon_path_source, "r") as fd:
    pokemon_list = json.load(fd)['pokemon_list']

def words(text):
    return re.findall(r'\w+', text.lower())

# NOTE: Since we're only correcting spelling of Pokemon,
# our dictionary is just the list of Pokemon
WORDS = Counter(pokemon_list)

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
