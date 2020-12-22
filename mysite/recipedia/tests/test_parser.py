import sys
import unittest


class TestParseIngredients(unittest.TestCase):

    def test_parse_ingredient(self):
        cases = {
            '1 cup flour': (1, 'cup', 'flour'),
            '3.5 tbsp sugar': (3.5, 'tablespoon', 'sugar'),
            '3/4 tsp baking soda': (0.75, 'teaspoon', 'baking soda'),
            '2 1/10 oz milk': (2.1, 'ounce', 'milk'),
            '1 and 1/2 gallons cider': (1.5, 'gallon', 'cider'),
            '¾ cup almonds': (0.75, 'cup', 'almonds'),
            '2 and ½ cups jello': (2.5, 'cup', 'jello'),
            '1 - 1.5 cups flour': (1.25, 'cup', 'flour'),
            '1-1 1/2 cups flour': (1.25, 'cup', 'flour'),
            '1 to 1 1/2 cups flour': (1.25, 'cup', 'flour'),
            '1- 1 ½ cups flour': (1.25, 'cup', 'flour'),
            '1 -1½ cups flour': (1.25, 'cup', 'flour'),
            '2 cups (226 grams) flour': (226, 'gram', 'flour'),
            '2 cups (226g) flour': (226, 'gram', 'flour'),
            '2 1/4 tsp. (1 packet) yeast': (2.25, 'teaspoon', 'yeast'),
            '8 oz (1 cup) water': (8, 'ounce', 'water')
        }

        for ingredient, (magnitude, unit, name) in cases.items():
            output = self.parser.parse_ingredient(ingredient)
            self.assertEqual(magnitude, output.quantity.magnitude)
            self.assertEqual(unit, str(output.quantity.units))
            self.assertEqual(name, output.name)
            self.assertEqual(output.ureg, self.parser.ureg)
            self.assertEqual(output.nlp, self.parser.nlp)

    def test_parse_number(self):
        cases = {
            '5': 5,
            '3.5': 3.5,
            '1/4': 0.25,
            '2 1/4': 2.25
        }
        for string, number in cases.items():
            output = self.parser.parse_number(string)
            self.assertEqual(number, output)

    def test_parse_expression(self):
        cases = {
            (2, 'eggs'): (2, 'dimensionless'),
            (1, 'cup'): (1, 'cup'),
            (3.5, 'tsp'): (3.5, 'teaspoon'),
        }
        for (number, word), (magnitude, units) in cases.items():
            output = self.parser.parse_expression(number, word)
            self.assertEqual(output.magnitude, magnitude)
            self.assertEqual(str(output.units), units)

    def test_parse_simple_qty(self):
        cases = {
            ('2', 'eggs, separated'): (2, 'dimensionless', 'eggs, separated'),
            ('1 1/2', 'cups heavy cream'): (1.5, 'cup', 'heavy cream')
        }
        for (number, phrase), (magnitude, unit, name) in cases.items():
            output = self.parser.parse_simple_qty(number, phrase)
            self.assertEqual(magnitude, output.quantity.magnitude)
            self.assertEqual(unit, str(output.quantity.units))
            self.assertEqual(name, output.name)

    def test_parse_qty_range(self):
        cases = {
            ('2', '3', 'eggs, separated'): (2.5, 'dimensionless', 'eggs, separated'),
            ('1', '1 1/2', 'teaspoons kosher salt'): (1.25, 'teaspoon', 'kosher salt')
        }
        for (num_a, num_b, phrase), (magnitude, unit, name) in cases.items():
            output = self.parser.parse_qty_range(num_a, num_b, phrase)
            self.assertEqual(magnitude, output.quantity.magnitude)
            self.assertEqual(unit, str(output.quantity.units))
            self.assertEqual(name, output.name)

    def test_parse_qty_alt(self):
        cases = {
            ('12', None, '1', 'carton', 'eggs'): (12, 'dimensionless', 'eggs'),
            ('1', 'teaspoon', '4', 'grams', 'kosher salt'): (4, 'gram', 'kosher salt'),
            ('4', 'grams', '1', 'teaspoon', 'kosher salt'): (4, 'gram', 'kosher salt')
        }
        for (num_a, word_a, num_b, word_b, name), (magnitude, unit, name) in cases.items():
            output = self.parser.parse_qty_alt(num_a, word_a, num_b, word_b, name)
            self.assertEqual(magnitude, output.quantity.magnitude)
            self.assertEqual(unit, str(output.quantity.units))
            self.assertEqual(name, output.name)


if __name__ == '__main__':
    sys.path.append('/Users/emily/recipe-parser/mysite/')
    from recipedia.recipe_parser import RecipeParser
    TestParseIngredients.parser = RecipeParser()
    unittest.main()
