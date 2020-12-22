"""
Represent an ingredient in a recipe.
"""

import pint
import re
import spacy
from spacy import displacy

from . import spacy_helpers


class Ingredient:

    def __init__(self, quantity, name, ureg, nlp):
        """
        Represent a recipe ingredient with its name and amount

        Args:
            quantity (pint.Quantity): 
            name: string describing the ingredient, e.g. 'macaroni pasta'
            ureg: pint.UnitRegistry instance, must be shared across all Ingredients
            nlp: spacy.Language object
        """
        self.quantity = quantity
        self.name = name.strip()
        self.ureg = ureg
        self.nlp = nlp

        # percent of recipe by volume that this ingredient makes up
        # gets overwritten once all Ingredients are instantiated
        self.percent = 0

        # process the ingredient name into a spacy Span
        # self.span = list(self.nlp(self.name).sents)[0]

        # try to identify the key word in the ingredient name
        # should be the syntactically highest noun in the name
        # if no nouns are identified, guess the syntactic root
        # self.base = spacy_helpers.get_top_noun(self.span) or self.span.root


    def has_words(self, words: str):
        """
        Return True if self.name contains the words in substring (may be separated)

        e.g. the substring 'green pepper' matches the name 'green bell pepper'
        """
        words = '.*'.join(words.split(' '))
        pattern = re.compile(words)
        match = re.search(pattern, self.name)
        if match:
            return True
        else:
            return False


    def __repr__(self):
        return self.name