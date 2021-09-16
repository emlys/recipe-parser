import re

import pint

from recipedia.ingredient import Ingredient


class IngredientParser:

    def __init__(self, ureg, nlp):
        self.ureg = ureg
        self.nlp = nlp

    def parse(self, ing):
        if isinstance(ing, list):
            return self.parse_ingredients(ing)
        else:
            return self.parse_ingredient(ing)

    def ingredient_from_components(self, amount, unit, name, id_):
        magnitude = self.parse_amount(amount)
        unit = self.parse_unit(unit)
        quantity = self.ureg.Quantity(magnitude, unit)
        return Ingredient(quantity, name, id_, self.ureg, self.nlp)

    def parse_ingredients(self, phrases):
        """Parse a list of phrases into a list of Ingredient objects.
        Args:
            phrases (list[string]): a list of ingredient descriptions
        Returns:
            list[Ingredient]: a list of Ingredient objects
        """
        ingredients = []
        id_ = 0
        for phrase in phrases:
            ingredients.append(self.parse_ingredient(phrase, id_))
            id_ += 1
        return ingredients

    def parse_amount(self, amount):
        """Parse an 'amount' string into a number.

        Args:
            amount (str):

        Returns:
            number
        """
        # Valid number formats:
        # integer: '2'
        # decimal: '1.5'
        # fraction: '1/3', '⅓'
        # mixed fraction: '2 1/2', '2 and 1/2', '2-1/2',
        #                 '2½', '2 ½', '2 and ½', '2-½'
        print('amount:', amount)
        # multi-character equivalents for fraction characters
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

        # Replace any unicode fractions with normal fractions
        for char, replacement in unicode_fracs.items():
            text = re.sub(rf'\s?{char}', f' {replacement}', amount)
        text = text.strip()

        # define some regular expressions to help identify numbers
        integer = r'(\d+)'
        fraction = f'{integer}/{integer}'
        # an integer and a fraction separated by ' ' or ' and ' or '-'
        # '-' can also be a range, but if it's an integer followed by a
        # fraction, it's safe to assume it's a mixed fraction.
        mixed_fraction = f'{integer}(?: | and |-)?{fraction}'
        decimal = rf'({integer}\.{integer})'

        number_parse = {
            integer: lambda match: float(match[1]),
            decimal: lambda match: float(match[1]),
            fraction: lambda match: float(match[1]) / float(match[2]),
            mixed_fraction: lambda match: (
                float(match[1]) + float(match[2]) / float(match[3]))
        }

        for pattern in [mixed_fraction, fraction, decimal, integer]:
            match = re.match(re.compile(pattern, text))
            if match:
                return number_parse[pattern](match)
        return None

    def parse_unit(self, unit):
        """Parse a unit string to a pint.Unit object.

        Args:
            unit (str): name of the unit

        Returns:
            pint.Unit object, or None if could not parse
        """
        try:  # try to parse the word as a unit
            return self.ureg.Unit(unit.lower())
        except pint.errors.UndefinedUnitError:
            return None

    def parse_ingredient(self, text, id_):
        """Parse an ingredient phrase into an Ingredient object.
        Args:
            text (string): the complete ingredient description e.g.
                '2 cups flour, sifted'
            id_ (int): a unique identifier for the Ingredient object.
        Returns:
            Ingredient object
        """
        # Valid number formats:
        # integer: '2'
        # decimal: '1.5'
        # fraction: '1/3', '⅓'
        # mixed fraction: '2 1/2', '2 and 1/2', '2-1/2',
        #                 '2½', '2 ½', '2 and ½', '2-½'
        print('ingredient:', text)
        # multi-character equivalents for fraction characters
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

        # Replace any unicode fractions with normal fractions
        for char, replacement in unicode_fracs.items():
            text = re.sub(f'\s?{char}', f' {replacement}', text)
        text = text.strip()

        # define some regular expressions to help identify numbers
        integer = '(\d+)'
        fraction = f'{integer}/{integer}'
        # an integer and a fraction separated by ' ' or ' and ' or '-'
        # '-' can also be a range, but if it's an integer followed by a
        # fraction, it's safe to assume it's a mixed fraction.
        mixed_fraction = f'{integer}(?: | and |-)?{fraction}'
        decimal = f'({integer}\.{integer})'
        # letter, hyphen, or period
        word = '[a-zA-Z-\.]+'
        word = '\S+'

        number_parse = {
            integer: lambda match: float(match[1]),
            decimal: lambda match: float(match[1]),
            fraction: lambda match: float(match[1]) / float(match[2]),
            mixed_fraction: lambda match: (
                float(match[1]) + float(match[2]) / float(match[3]))

        }

        def match_number(pattern, text):
            for num_pattern in [mixed_fraction, fraction, decimal, integer]:
                match = re.match(re.compile(pattern.format(
                    num_pattern=num_pattern, word=word)), text)
                if match:
                    magnitude = number_parse[num_pattern](match)
                    try:  # try to parse the word as a unit
                        units = self.ureg.Unit(match['unit'].lower())
                        quantity = magnitude * units
                        remainder = match['tail']
                    except:  # if it's not a unit, return a unitless Quantity
                        quantity = self.ureg.Quantity(magnitude)
                        remainder = match['remainder']
                    return quantity, remainder
            return None, None

        quantity_a, remainder_a = match_number(
            '{num_pattern} ?(?P<remainder>(?P<unit>{word}) ?(?P<tail>.*))',
            text)
        if not quantity_a:
            return Ingredient(self.ureg.Quantity(0), text, id_, self.ureg, self.nlp)

        # match against range format
        quantity_b, remainder_b = match_number(
            '(?:- ?|to ){num_pattern} ?(?P<remainder>(?P<unit>{word})(?P<tail>.*))',
            remainder_a)
        if quantity_b:
            # i want to know if this ever isn't dimensionless
            assert quantity_a.dimensionless
            # if the measurement is given as a range, use the average
            avg_quantity = self.ureg.Quantity(
                (quantity_a.magnitude + quantity_b.magnitude) / 2,
                quantity_b.units
            )
            return Ingredient(avg_quantity, remainder_b, id_, self.ureg, self.nlp)

        # match against alternate measurement format
        quantity_c, remainder_c = match_number(
            ' ?\(({num_pattern}) ?(?P<unit>{word})?\)(?P<tail>(?P<remainder>.*))',
            remainder_a)
        if quantity_c:
            # prefer measurements of mass; otherwise use the first measurement
            if (str(quantity_c.dimensionality) == '[mass]' and
                    str(quantity_a.dimensionality) != '[mass]'):
                return Ingredient(quantity_c, remainder_c, id_, self.ureg, self.nlp)
            else:
                return Ingredient(quantity_a, remainder_c, id_, self.ureg, self.nlp)

        return Ingredient(quantity_a, remainder_a, id_, self.ureg, self.nlp)
