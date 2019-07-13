from enum import Enum

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzywuzzy import utils
import heapq
import re


def pre(string: str):
    s = string.lower()
    s = s.strip()
    return s


def is_empty(word: str):
    s = re.sub(r'\W+', '', word)
    if s == '':
        return True
    return False


def fp_ratio(s1, s2, force_ascii=True, full_process=True):
    """
    Return a measure of the sequences' similarity between 0 and 100, using fuzz.ratio and fuzz.partial_ratio.
    """
    if full_process:
        p1 = utils.full_process(s1, force_ascii=force_ascii)
        p2 = utils.full_process(s2, force_ascii=force_ascii)
    else:
        p1 = s1
        p2 = s2

    if not utils.validate_string(p1):
        return 0
    if not utils.validate_string(p2):
        return 0

    # should we look at partials?
    try_partial = True
    partial_scale = .9

    base = fuzz.ratio(p1, p2)
    len_ratio = float(max(len(p1), len(p2))) / min(len(p1), len(p2))

    # if strings are similar length, don't use partials
    if len_ratio < 1.5:
        try_partial = False

    # if one string is much much shorter than the other
    if len_ratio > 8:
        partial_scale = .6

    if try_partial:
        partial = fuzz.partial_ratio(p1, p2) * partial_scale
        return utils.intr(max(base, partial))
    else:
        return utils.intr(base)


def get_match(word_list: list, word: str, score_cutoff: int = 80):
    """Uses fuzzywuzzy to see if word is close to entries in word_list

    Returns a tuple of (MATCH, SCORE)
    """

    try:
        result = process.extractOne(
            word, word_list, processor=pre, scorer=fuzz.ratio, score_cutoff=score_cutoff)
    except:
        return (None, None)
    if not result:
        return (None, None)
    return result


def get_matches(word_list: list, word: str, score_cutoff: int = 80, limit: int = 10):
    """Uses fuzzywuzzy to see if word is close to entries in word_list

    Returns a list of tuples with (MATCH, SCORE)
    """
    best_list = process.extractWithoutOrder(word, word_list, pre, fp_ratio, score_cutoff)
    sorted_list = heapq.nlargest(limit, best_list, key=lambda i: i[1])
    great_matches = [x for x in sorted_list if x[1] >= 95]
    if great_matches:
        return great_matches
    good_matches = [x for x in sorted_list if x[1] >= 90]
    if good_matches:
        return good_matches
    else:
        return sorted_list


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
