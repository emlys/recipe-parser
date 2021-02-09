"""
Represent an ingredient in a recipe.
"""

import pint
import re
import spacy
from spacy import displacy

from . import spacy_helpers
from .node import Node


class Ingredient(Node):

    def __init__(self, quantity, name, id_, ureg, nlp):
        """
        Represent a recipe ingredient with its name and amount

        Args:
            quantity (pint.Quantity): 
            name (string): describes the ingredient, e.g. 'macaroni pasta'
            id_ (int): unique identifier for this ingredient
            ureg (pint.UnitRegistry instance): shared across all Ingredients
            nlp (spacy.Language): shared across all Ingredients
        """
        super().__init__(id_)
        self.quantity = quantity
        self.name = name.strip().lower()  # ignore case and trailing whitespace
        self.nlp = nlp

        # percent of recipe by volume that this ingredient makes up
        # gets overwritten once all Ingredients are instantiated
        self.percent = 0

        # process the ingredient name into a spacy Span
        self.span = list(self.nlp(self.name).sents)[0]

        # try to identify the key word in the ingredient name
        # should be the syntactically highest noun in the name
        # if no nouns are identified, guess the syntactic root
        self.base = spacy_helpers.get_top_noun(self.span) or self.span.root


    def has_words(self, words: str):
        """
        Return True if self.name contains the words in substring (may be separated)

        e.g. the substring 'green pepper' matches the name 'green bell pepper'
        """
        words = words.split(' ')
        for word in words:
            if word not in self.name:
                return False
        return True

    def num_matching_words(self, words):
        count = 0
        for word in words:
            if word in self.name:
                count += 1
        return count

    def as_dict(self):
        """Return a dictionary representation of self, for JSON responses."""
        return {
            'name': self.name,
            'magnitude': self.quantity.magnitude,
            'unit': str(self.quantity.units)
        }


    def __repr__(self):
        return str(self.quantity.magnitude) + ':' + str(self.quantity.units) + ':' + self.name
