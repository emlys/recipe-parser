import pint
import re
import requests
import spacy
from bs4 import BeautifulSoup

from recipedia.ingredient import Ingredient
from recipedia.recipe2 import Recipe

headers = {'User-Agent': 'Mozilla/5.0 (compatible)'}
class RecipeParser:

    def __init__(self):
        """Instantiate NLP package and unit registry to use in Recipes"""
        print('Loading spacy package...')
        self.nlp = spacy.load('en_core_web_md')
        print('done. Loading pint unit registry...')
        self.ureg = pint.UnitRegistry()
        print('done.')

# ---- Whole recipe parsing ---------------------------------------------------

    def parse(self, url):
        """
        Try to parse the webpage into a Recipe object.

        Pages made with WordPress Recipe Maker and certain popular recipe
        websites are supported.

        Args:
            url: URL of webpage to parse
        Returns:
            Recipe object
        """
        # get what's between the second and third slashes
        domain = url.split('/')[2]
        response = requests.get(url, headers=headers)
        if response.status_code not in [200, 201]:
            print(f'GET request to {url} failed: code {response.status_code}')
        soup = BeautifulSoup(response.text, 'lxml')

        # because some of the formats use chained functions, it's not
        # convenient to implement a lazy dictionary.
        # going with if/else for now
        ingredient_tags, instruction_tags = None, None
        if domain == 'www.allrecipes.com':
            ingredient_tags = soup.find_all('span', class_='ingredients-item-name')
            instruction_tags = soup.find('ul', class_='instructions-section').find_all('p')
        elif domain == 'www.foodnetwork.com':
            # first tag is 'select all' so remove it
            ingredient_tags = soup.find_all('span', class_='o-Ingredients__a-Ingredient--CheckboxLabel')[1:]
            instruction_tags = soup.find_all('li', class_='o-Method__m-Step')
        elif domain == 'www.tasteofhome.com':
            ingredient_tags = soup.find('ul', class_='recipe-ingredients__list').find_all('li')
            instruction_tags = soup.find_all('li', class_='recipe-directions__item')
        elif domain == 'www.simplyrecipes.com':
            ingredient_tags = soup.find_all('li', class_='ingredient')
            instruction_tags = soup.find(class_='recipe-method').find_all('p')
        elif domain == 'www.thespruceeats.com':
            ingredient_tags = soup.find_all('li', class_='ingredient')
            instruction_tags = soup.find(class_='comp section--instructions section').find_all('p', class_='comp mntl-sc-block mntl-sc-block-html')
        elif domain == 'www.epicurious.com':
            ingredient_tags = soup.find_all('li', class_='ingredient')
            instruction_tags = soup.find_all('p', class_='preparation_step')
        elif domain == 'www.food.com':
            ingredient_tags = soup.find_all('div', class_='recipe-ingredients__ingredient')
            instruction_tags = soup.find_all('li', class_='recipe-directions__step')

        if ingredient_tags and instruction_tags:
            # make a list of Ingredient objects
            ingredients = self.parse_ingredients([i.get_text().strip() for i in ingredient_tags])
            instructions_list = []
            # Make sure sentences are separated by a period to help spaCy out
            for i in instruction_tags:
                text = i.get_text().strip()
                if not text.endswith('.'):
                    text += '.'
                instructions_list.append(text)
            instructions = ' '.join(instructions_list)
            # Replace all colons and semicolons with periods. spaCy seems to do
            # better when these are separate sentences.
            instructions = instructions.replace(';', '.')
            instructions = instructions.replace(':', '.')
            return Recipe(ingredients, instructions, self.ureg, self.nlp)

        if self.is_wordpress_recipe(soup):
            return self.parse_wordpress_recipe(soup)
        else:
            print('unknown format')

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
        id_ = 0
        for tag in ingredient_tags:
            amount = tag.find('span', class_='wprm-recipe-ingredient-amount')
            unit = tag.find('span', class_='wprm-recipe-ingredient-unit')
            name = tag.find('span', class_='wprm-recipe-ingredient-name')
            notes = tag.find('span', class_='wprm-recipe-ingredient-notes')

            amount, unit, name, notes = [attr.get_text().lower() if attr else None for attr in [amount, unit, name, notes]]
            print('amount, quantity', amount, unit)
            quantity = self.ureg.Quantity(amount or 0, unit)
            ingredients.append(self.parse_ingredient(f'{amount} {unit} {name} {notes}', id_))
            # ingredients.append(Ingredient(quantity, name, id_, self.ureg, self.nlp))
            id_ += 1

        instructions = ' '.join([tag.get_text() for tag in instruction_tags])

        r = Recipe(ingredients, instructions, self.ureg, self.nlp)

        return r




# ---- Ingredient parsing -----------------------------------------------------

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

    def parse_ingredient(self, text, id_):
        """Parse an ingredient phrase into an Ingredient object.
        Args:
            text (string): the complete ingredient description e.g. '2 cups flour, sifted'
            id_ (int): a unique identifier for the Ingredient object.
        Returns:
            Ingredient object
        """
        # Valid number formats:
        # integer: '2'
        # decimal: '1.5'
        # fraction: '1/3', '⅓'
        # mixed fraction: '2 1/2', '2 and 1/2', '2-1/2', '2½', '2 ½', '2 and ½', '2-½'
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
            mixed_fraction: lambda match: float(match[1]) + float(match[2]) / float(match[3])

        }


        def match_number(pattern, text):
            for num_pattern in [mixed_fraction, fraction, decimal, integer]:
                match = re.match(re.compile(pattern.format(num_pattern=num_pattern, word=word)), text)
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

