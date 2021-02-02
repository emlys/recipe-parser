import pint
import spacy
import sys
import unittest

sys.path.append('/Users/emily/recipe-parser/mysite/')
from recipedia.ingredient import Ingredient
from recipedia.recipe import Recipe


class TestParseSteps(unittest.TestCase):

    ureg = pint.UnitRegistry()
    nlp = spacy.load('en_core_web_md')

    def test_exact_match(self):
        """The simplest case: exact string matching"""
        ingredients = [
            Ingredient(
                self.ureg.Quantity(magnitude, unit),
                name, 
                self.ureg, 
                self.nlp
            ) for (magnitude, unit, name) in [
                (1/3, 'cup', 'flour'),
                (1, None, 'onion'),
                (4, 'tablespoon', 'butter'),
                (1/2, 'teaspoon', 'poultry seasoning'),
                (1/4, 'teaspoon', 'thyme')
            ]
        ]

        instructions = ('Cook onion and butter over medium low heat until '
            'tender, about 5 minutes. Add flour, poultry seasoning & thyme.')

        recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)

        self.assertEqual(len(recipe.graph), 2)  # 2 steps
        self.assertEqual(recipe.graph[0].ingredients, {1, 2})
        self.assertEqual(recipe.graph[1].ingredients, {0, 3, 4})

    def test_substring_match(self):
        """Each word of the reference is a substring of the ingredient."""
        ingredients = [
            Ingredient(
                self.ureg.Quantity(magnitude, unit),
                name, 
                self.ureg, 
                self.nlp
            ) for (magnitude, unit, name) in [
                (1, None, 'orange, juiced and zested'),
                (1, None, 'orange bell pepper'),
                (1, None, 'green bell pepper'),
                (1/4, 'teaspoon', 'black pepper')
            ]
        ]

        instructions = ('Chop the orange pepper and green pepper. Mix '
            'the black pepper, orange zest and juice.')
        recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)

        self.assertEqual(len(recipe.graph), 2)  # 2 steps
        self.assertEqual(recipe.graph[0].ingredients, {1, 2})
        self.assertEqual(recipe.graph[1].ingredients, {3, 0})

    def test_preposition_object_match(self):
        """Identify ingredients that are the object of a preposition."""
        ingredients = [
            Ingredient(
                self.ureg.Quantity(magnitude, unit),
                name, 
                self.ureg, 
                self.nlp
            ) for (magnitude, unit, name) in [
                (8, 'ounce', 'chocolate'),
                (1, 'cup', 'heavy cream'),
                (1, 'cup', 'mini marshmallows')
            ]
        ]
        instructions = ('Stir the chocolate into the heavy cream. '
            'Pour over the mini marshmallows.')
        recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)
        
        self.assertEqual(len(recipe.graph), 2)  # 2 steps
        self.assertEqual(recipe.graph[0].ingredients, {0, 1})
        self.assertEqual(recipe.graph[1].ingredients, {0, 1, 2})

if __name__ == '__main__':
    unittest.main()
