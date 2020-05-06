"""
Represent an ingredient in a recipe.
"""

import pint
import re
import spacy


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

        
        print(name, quantity, unit)
        if quantity and unit:
            
            # Sometimes recipes use fraction characters like '¼'
            # To parse these we need to convert them to standard fractions like '1/4'
            quantity = self.replace_unicode_fractions(quantity)

            self.quantity = ureg.parse_expression(' '.join([quantity, unit]))
        else:
            self.quantity = pint.Quantity(0)

        self.percent = 0

        self.span = list(self.nlp(self.name).sents)[0]

        for token in self.span:
                print(token, token.pos_, token.tag_, token.dep_)

        if self.span.root.pos_ == 'NOUN' or self.span.root.pos_ == 'PROPN':
            self.base = self.span.root
        else:
            for token in self.span:
                print(token.dep_)
            self.base = [token for token in self.span if token.dep_ == 'dobj'][0]

        print(self.name, self.base)
        

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

    def __str__(self):
        return self.name