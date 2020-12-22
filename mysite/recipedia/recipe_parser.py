import argparse
import pint
import re
import requests
import spacy
from functools import partial
from fractions import Fraction
from bs4 import BeautifulSoup

from recipedia.ingredient import Ingredient
from recipedia import recipe


class RecipeParser:

    def __init__(self):
        """Instantiate NLP package and unit registry to use in Recipe"""

        print('Loading spacy package...')
        self.nlp = spacy.load('en_core_web_lg')
        print('done. Loading pint unit registry...')
        self.ureg = pint.UnitRegistry()
        print('done.')

    def parse(self, url):
        """
        Try to parse the webpage as a WordPress recipe.
        
        Parameters:
            url: URL of webpage to parse
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')

        if self.is_wordpress_recipe(soup):
            self.parse_wordpress_recipe(soup)
        else:
            print('Recipe is not in WordPress Recipe Maker format')

        def soup_find_all(tag, class_, soup):
            return soup.find_all(tag, class_)

        def get_tasteofhome_ingredients(soup):
            return soup.find('ul', 'recipe-ingredients__list').find_all('li')

        def get_simplyrecipes_instructions(soup):
            return soup.find(class_='recipe-method instructions').find_all('p')

        known_formats = {
            'www.allrecipes.com': {
                'ingredients':  partial(soup_find_all, 'span', 'ingredients-item-name'),
                'instructions': partial(soup_find_all, 'li', 'instructions-section-item')},
            'www.foodnetwork.com': {
                'ingredients':  partial(soup_find_all, 'span', 'o-Ingredients__a-Ingredient--CheckboxLabel'),
                'instructions': partial(soup_find_all, 'li', 'o-Method__m-Step')},
            'www.tasteofhome.com': {
                'ingredients':  get_tasteofhome_ingredients,
                'instructions': partial(soup_find_all, 'li', 'recipe-directions__item')},
            'www.simplyrecipes.com': {
                'ingredients':  partial(soup.find_all, 'li', 'ingredient'),
                'instructions': get_simplyrecipes_instructions},
            'www.thespruceeats.com': {
                'ingredients':  partial(soup_find_all, 'li', 'ingredient'),
                'instructions': partial(soup_find_all, 'p', 'comp mntl-sc-block mntl-sc-block-html')},
            'www.epicurious.com': {
                'ingredients':  partial(soup_find_all, 'li', 'ingredient'),
                'instructions': partial(soup_find_all, 'li', 'preparation_step')},
            'www.food.com': {
                'ingredients':  partial(soup_find_all, 'div', 'recipe-ingredients__ingredient'),
                'instructions': partial(soup_find_all, 'li', 'recipe-directions__step')}
        }

        
        domain = url.split('/')[2]  # get what's between the second and third slashes
        # if domain in known_formats:

# ---- Ingredient parsing -----------------------------------------------------

    def parse_ingredient(self, text):
        """Parse an ingredient phrase into an Ingredient object.
        Args:
            text (string): the complete ingredient description e.g. '2 cups flour, sifted'
        Returns:
            Ingredient object
        """

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
            text = re.sub(f' ?{char}', f' {replacement}', text)
        text = text.strip()

        # define some regular expressions to help identify numbers
        integer = '\d+'
        fraction = f'{integer}/{integer}'
        # an integer and a fraction separated by ' ' or ' and '
        mixed_fraction = f'{integer} (and )?{fraction}'
        decimal = f'{integer}\.{integer}'
        number = f'{mixed_fraction}|{fraction}|{decimal}|{integer}'


        word = '\D+'
        # two numbers separated by a dash, possibly with spaces, or ' to '
        qty_range = f'({number})( ?- ?| to )({number})'

        # quantity with alternate measurement in parentheses e.g. '2 cups (226g)'
        qty_alt = f'({number})({word})\(({number})({word})\)'
        # TODO: handle nested alternate and range e.g. '2-3 cups (226-360g)'


        # First check for alternate measurement format
        match = re.match(re.compile(f'{qty_alt}(.+)'), text)
        if match:
            return self.parse_qty_alt(match[1], match[3], match[4], match[6], match[7])

        # If that doesn't match, check for range format
        match = re.match(re.compile(f'{qty_range}(.+)'), text)
        if match:
            return self.parse_qty_range(match[1], match[4], match[6])

        # If that doesn't match, check for simple format
        match = re.match(re.compile(f'({number})(.+)'), text)
        if match:
            return self.parse_simple_qty(match[1], match[3])

        # If that doesn't match, use the unitless format
        return Ingredient(quantity=self.ureg.Quantity(0), name=text, ureg=self.ureg, nlp=self.nlp)


    def parse_number(self, phrase):
        """Parse a number phrase into a float.
        Args:
            phrase (string): representation of a numeric value. Accepts:
                integers e.g. '2'; fractions e.g. '1/3'; decimals e.g. '1.5';
                mixed fractions e.g. '1 1/3' or '1 and 1/3'
        Returns:
            float
        """# define some regular expressions to help identify numbers
        integer = '\d+'
        decimal = f'{integer}\.{integer}'
        fraction = f'({integer})/({integer})'
        # an integer and a fraction separated by ' ' or ' and '
        mixed_fraction = f'({integer}) (and )?{fraction}'
        number = f'{mixed_fraction}|{fraction}|{decimal}|{integer}'

        match = re.match(re.compile(mixed_fraction), phrase)
        if match:
            return float(match[1]) + float(match[3]) / float(match[4])
        match = re.match(re.compile(fraction), phrase)
        if match:
            return float(match[1]) / float(match[2])
        return float(phrase)

    def parse_expression(self, number, word):
        """Wrapper around ureg.parse_expression to handle non-units.
        Args:
            number (float): amount of ingredient
            word (string): single word following the number that may or may 
                not be a unit, e.g. '2 *eggs*'; '2 *cups*'
        Returns:
            pint.Quantity with magnitude = number, 
                units = word if word is a unit, otherwise unitless.
        """
        
        try:
            # try to parse the word as a unit
            return number * self.ureg.parse_expression(word)
        except pint.errors.UndefinedUnitError:
            # if it's not a unit, return a unitless quantity, and keep the word separate
            return self.ureg.Quantity(number)

    def parse_simple_qty(self, num_a, text):
        """Parse a simple ingredient phrase to an Ingredient.
        Args:
            num_a (string): representation of the first number e.g. '1.5'
            text (string): remaining text of the ingredient phrase
        Returns:
            Ingredient object
        """
        words = text.split()
        head, tail = words[0], ' '.join(words[1:])
        float_a = self.parse_number(num_a)
        qty = self.parse_expression(float_a, head)

        if str(qty.units) == 'dimensionless':
            return Ingredient(quantity=qty, name=text, ureg=self.ureg, nlp=self.nlp)
        else:
            return Ingredient(quantity=qty, name=tail, ureg=self.ureg, nlp=self.nlp)


    def parse_qty_range(self, num_a, num_b, text):
        """Parse an ingredient phrase with a quantity range to an Ingredient
        Args:
            num_a (string): representation of the first number e.g. '1.5'
            num_b (string): representation of the first number e.g. '1.5'
            text (string): remaining text of the ingredient phrase
        Returns:
            Ingredient object
        """
        words = text.split()
        head, tail = words[0], ' '.join(words[1:])

        # Take the average of the range
        float_a, float_b = self.parse_number(num_a), self.parse_number(num_b)
        avg = (float_a + float_b) / 2

        qty = self.parse_expression(avg, head)
        if str(qty.units) == 'dimensionless':
            return Ingredient(quantity=qty, name=text, ureg=self.ureg, nlp=self.nlp)
        else:
            return Ingredient(quantity=qty, name=tail, ureg=self.ureg, nlp=self.nlp)

    def parse_qty_alt(self, num_a, word_a, num_b, word_b, text):
        """ Parse an ingredient phrase with alternate quantity to an Ingredient

        Prefers units of mass over other dimensionalities; otherwise prefers
        the first quantity. E.g.
            '2 cups (226g) flour, sifted' -> 
                Ingredient(Quantity(226, 'grams'), 'flour, sifted')
            '5 cups (1 package) noodles' ->
                Ingredient(Quantity(5, 'cups'), 'noodles')
        Args:
            num_a (string): representation of the first number e.g. '1.5', '1 1/2'
            word_a (string): word following the first number; may or may not be a unit
            num_b (string): representation of the alternate number e.g. '1.5', '1 1/2'
            word_b (string): word following the alternate number; may or may not be a unit
            text (string): remaining ingredient text
        Returns:
            Ingredient object storing one of the two quantities and remaining text
        """
        float_a, float_b = self.parse_number(num_a), self.parse_number(num_b)
        qty_a = self.parse_expression(float_a, word_a)
        qty_b = self.parse_expression(float_b, word_b)

        # If the second quantity measures mass and the first doesn't, use the
        # second one. Otherwise use the first.
        if (str(qty_a.units.dimensionality) != '[mass]' and 
            str(qty_b.units.dimensionality) == '[mass]'):
            return Ingredient(quantity=qty_b, name=text, ureg=self.ureg, nlp=self.nlp)
        else:
            return Ingredient(quantity=qty_a, name=text, ureg=self.ureg, nlp=self.nlp)






    def is_wordpress_recipe(self, soup):
        """
        Return True if soup contains a WordPress recipe

        Parameters:
            soup: BeautifulSoup representation of webpage with recipe
        Returns:
            bool
        """
        ingr = 'wprm-recipe-ingredients-container'
        inst = 'wprm-recipe-instructions-container'
        if soup.find(class_=ingr) and soup.find(class_=inst):
            return True
        return False

    def parse_wordpress_recipe(self, soup):
        """
        Read and interpret ingredients and instructions from a WordPress recipe

        Parameters:
            soup: BeautifulSoup representation of webpage with recipe
        Returns:
            Recipe object representation
        """
        ingredient_tags = soup.find_all('li', class_='wprm-recipe-ingredient')
        instruction_tags = soup.find_all('div', class_='wprm-recipe-instruction-text')

        ingredients, instructions = [], []

        for tag in ingredient_tags:
            amount = tag.find('span', class_='wprm-recipe-ingredient-amount')
            unit = tag.find('span', class_='wprm-recipe-ingredient-unit')
            name = tag.find('span', class_='wprm-recipe-ingredient-name')
            notes = tag.find('span', class_='wprm-recipe-ingredient-notes')

            amount, unit, name, notes = [attr.get_text().lower() if attr else None for attr in [amount, unit, name, notes]]

            ingredients.append(Ingredient(amount, unit, name, notes, self.ureg, self.nlp))

        instructions = ' '.join([tag.get_text() for tag in instruction_tags])

        r = recipe.Recipe(ingredients, instructions, self.ureg, self.nlp)

        return r


    def parse_allrecipes_recipe(self, soup):
        ingredient_tags = soup.find_all('span', class_='ingredients-item-name')
        instruction_tags = soup.find_all('li', class_='instructions-section-item')

        ingredients = [i.get_text().strip() for i in ingredient_tags]
        instructions = [i.find('p').get_text().strip() for i in instruction_tags]        

        

    def parse_foodcom_recipe(self, soup):
        ingredient_tags = soup.find_all('div', class_='recipe-ingredients__ingredient')
        'recipe-ingredients__ingredient-quantity'
        'recipe-ingredients__ingredient-parts'

        


def main():
    """Entrypoint for recipe parser"""

    # parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL of recipe to parse')
    args = parser.parse_args()

    RecipeParser().parse(args.url)


if __name__ == '__main__':
    main()
