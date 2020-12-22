import sys
import unittest


class TestParseIngredients(unittest.TestCase):

    def test_ingredients(self):
        cases = {
            '1 cup flour': (1, 'cup', 'flour'),
            '3.5 tbsp sugar': (3.5, 'tablespoon', 'sugar'),
            '3/4 tsp baking soda': (0.75, 'teaspoon', 'baking soda'),
            '2 1/10 oz milk': (2.1, 'ounce', 'milk'),
            '1 and 1/2 gallons cider': (1.5, 'gallon', 'cider'),
            '¾ cup almonds': (0.75, 'cup', 'almonds'),
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

        parser = RecipeParser()
        for ingredient, (magnitude, unit, name) in cases.items():
            output = parser.parse_ingredient(ingredient)
            self.assertEqual(magnitude, output.quantity.magnitude)
            self.assertEqual(unit, str(output.quantity.units))
            self.assertEqual(name, output.name)


if __name__ == '__main__':
    sys.path.append('/Users/emily/recipe-parser/mysite/')
    from recipedia.recipe_parser import RecipeParser
    unittest.main()
