"""
Represent an ingredient in a recipe.
"""

import pint
import re
import spacy
from spacy import displacy

from spacy_helpers import get_top_noun


class Ingredient:

    def __init__(self, quantity, unit, name, notes, ureg, nlp):
        """
        Represent a recipe ingredient with its name and amount

        quantity: string representing the unitless amount of the ingredient,
            e.g. '16' or '1 1/2'
        unit: string representing the unit of measurement of the ingredient,
            e.g 'cups' or 'tbsp'
        name: string describing the ingredient, e.g. 'macaroni pasta'
        notes: string with additional information, e.g. 'shredded'
        ureg: pint.UnitRegistry instance, must be shared across all Ingredients
        nlp: spacy.Language object
        """
        self.name = name
        self.notes = notes or ''
        self.ureg = ureg
        self.nlp = nlp

        
        if quantity and unit:
            # instantiate a pint.Quantity
            self.quantity = self.parse_quantity(quantity, unit)
        else:
            # if no quantity given, assume 0
            self.quantity = pint.Quantity(0)

        # percent of recipe by volume that this ingredient makes up
        # gets overwritten once all Ingredients are instantiated
        self.percent = 0

        # process the ingredient name into a spacy Span
        self.span = list(self.nlp(self.name).sents)[0]

        # try to identify the key word in the ingredient name
        # should be the syntactically highest noun in the name
        # if no nouns are identified, guess the syntactic root
        self.base = get_top_noun(self.span) or self.span.root


    def parse_quantity(self, quantity: str, unit: str) -> pint.Quantity:
        """Parse quantity and unit into a pint.Quantity"""

        # Sometimes recipes use fraction characters like '¼'
        # To parse these we need to convert them to standard fractions like '1/4'
        quantity = self.replace_unicode_fractions(quantity)

        # define some regular expressions to help identify numbers
        integer = '\d+'
        fraction = '{}/{}'.format(integer, integer)
        mixed_fraction = '{} {}'.format(integer, fraction)
        decimal = '{}\.{}'.format(integer, integer)
        number = '|'.join([mixed_fraction, fraction, decimal, integer])

        # two numbers separated by a dash, possibly with spaces
        quantity_range = '({}) ?- ?({})'.format(number, number)

        # check if the quantity is a range e.g. "1.5 - 2 cups flour"
        pattern = re.compile(quantity_range)
        match = pattern.match(quantity)

        # if it is, take the middle value
        if match:
            low_bound = self.check_for_mixed_fraction(match.group(1), unit)
            high_bound = self.check_for_mixed_fraction(match.group(2), unit)
            return (low_bound + high_bound) / 2
        else:
            return self.check_for_mixed_fraction(quantity, unit)


    def check_for_mixed_fraction(self, quantity: str, unit: str):
        """
        Return quantity and unit as a Quantity, accounting for mixed fractions.
        """
        integer = '\d+'
        fraction = '{}/{}'.format(integer, integer)
        mixed_fraction = '({}) ({})'.format(integer, fraction)

        pattern = re.compile(mixed_fraction)
        match = pattern.match(quantity)
        if match:
            integer_part = self.parse_expression(match.group(1), unit)
            fraction_part = self.parse_expression(match.group(2), unit)
            return integer_part + fraction_part
        else:
            return self.parse_expression(quantity, unit)


    def parse_expression(self, quantity: str, unit: str) -> pint.Quantity:
        """Parse quantity and unit into a pint.Quantity"""
        try:
            return self.ureg.parse_expression(quantity + ' ' + unit)
        except pint.errors.UndefinedUnitError:
            # if unit isn't recognized, instantiate a dimensionless quantity
            return self.ureg.Quantity(quantity)

        
    def replace_unicode_fractions(self, quantity):
        """Replace fraction characters with multi-character equivalents"""
        unicode_fracs = {
            '½': '1/2',
            '⅓': '1/3',
            '⅔': '2/3',
            '¼': '1/4',
            '¾': '3/4',
            '⅛': '1/8',
            '⅜': '3/8',
            '⅝': '5/8',
            '⅞': '7/8'
        }

        for char, replacement in unicode_fracs.items():
            pattern = re.compile(char)
            quantity = re.sub(pattern, replacement, quantity)

        return quantity


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