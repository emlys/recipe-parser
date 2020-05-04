"""
Represent an ingredient in a recipe.
"""

import pint
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


        if quantity and unit:
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
        

    def __str__(self):
        return self.name