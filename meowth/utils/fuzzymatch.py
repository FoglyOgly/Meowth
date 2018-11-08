from enum import Enum

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_match(word_list: list, word: str, score_cutoff: int = 80):
    """Uses fuzzywuzzy to see if word is close to entries in word_list

    Returns a tuple of (MATCH, SCORE)
    """
    result = process.extractOne(
        word, word_list, scorer=fuzz.ratio, score_cutoff=score_cutoff)
    if not result:
        return (None, None)
    return result

def get_matches(word_list: list, word: str, score_cutoff: int = 80):
    """Uses fuzzywuzzy to see if word is close to entries in word_list

    Returns a list of tuples with (MATCH, SCORE)
    """
    return process.extractBests(
        word, word_list, scorer=fuzz.ratio, score_cutoff=score_cutoff)

class FuzzyEnum(Enum):
    """Enumeration with fuzzy-matching classmethods."""

    @classmethod
    def name_list(cls):
        return list(cls.__members__.keys())

    @classmethod
    def value_list(cls):
        return [e.value for e in cls]

    @classmethod
    def match_name(cls, arg):
        word_list = cls.name_list()
        match = get_match(word_list, arg, score_cutoff=80)[0]
        return cls[match]

    @classmethod
    def match_value(cls, arg):
        word_list = cls.value_list()
        match = get_match(word_list, arg, score_cutoff=80)[0]
        return cls(match)
