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

    # def test_exact_match(self):
    #     """The simplest case: exact string matching"""
    #     ingredients = [
    #         Ingredient(
    #             self.ureg.Quantity(magnitude, unit),
    #             name, 
    #             i,
    #             self.ureg, 
    #             self.nlp
    #         ) for i, (magnitude, unit, name) in enumerate([
    #             (1/3, 'cup', 'flour'),
    #             (1, None, 'onion'),
    #             (4, 'tablespoon', 'butter'),
    #             (1/2, 'teaspoon', 'poultry seasoning'),
    #             (1/4, 'teaspoon', 'thyme')
    #         ])
    #     ]

    #     instructions = ('Cook onion and butter about 5 minutes. '
    #         'Add flour, poultry seasoning & thyme.')

    #     recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)

    #     self.assertEqual(len(recipe.graph), 2)  # 2 steps
    #     self.assertEqual(recipe.graph[0].ingredients, {ingredients[1], ingredients[2]})
    #     self.assertEqual(recipe.graph[1].ingredients, {ingredients[0], ingredients[3], ingredients[4]})

    # def test_substring_match(self):
    #     """Each word of the reference is a substring of the ingredient."""
    #     ingredients = [
    #         Ingredient(
    #             self.ureg.Quantity(magnitude, unit),
    #             name, 
    #             i, 
    #             self.ureg, 
    #             self.nlp
    #         ) for i, (magnitude, unit, name) in enumerate([
    #             (1, None, 'lime, juiced and zested'),
    #             (1, None, 'orange bell pepper'),
    #             (1/4, 'teaspoon', 'black pepper')
    #         ])
    #     ]

    #     instructions = ('Chop the orange pepper. '
    #         'Mix the black pepper, zest and juice.')
    #     recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)

    #     self.assertEqual(len(recipe.graph), 2)  # 2 steps
    #     self.assertEqual(recipe.graph[0].ingredients, {ingredients[1]})
    #     self.assertEqual(recipe.graph[1].ingredients, {ingredients[0], ingredients[2]})

    # def test_preposition_object_match(self):
    #     """Identify ingredients that are the object of a preposition."""
    #     ingredients = [
    #         Ingredient(
    #             self.ureg.Quantity(magnitude, unit),
    #             name, 
    #             i,
    #             self.ureg, 
    #             self.nlp
    #         ) for i, (magnitude, unit, name) in enumerate([
    #             (8, 'ounce', 'chocolate'),
    #             (1, 'cup', 'heavy cream'),
    #             (1, 'cup', 'mini marshmallows')
    #         ])
    #     ]
    #     instructions = ('Stir the chocolate into the heavy cream. '
    #         'Combine with the mini marshmallows.')
    #     recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)
        
    #     self.assertEqual(len(recipe.graph), 2)  # 2 steps
    #     self.assertEqual(recipe.graph[0].ingredients, {ingredients[0], ingredients[1]})
    #     self.assertEqual(recipe.graph[1].ingredients, {ingredients[0], ingredients[1], ingredients[2]})

    # def test_choose_best_match(self):
    #     """Identify ingredients with overlapping names."""
    #     ingredients = [
    #         Ingredient(
    #             self.ureg.Quantity(magnitude, unit),
    #             name,
    #             i, 
    #             self.ureg, 
    #             self.nlp
    #         ) for i, (magnitude, unit, name) in enumerate([
    #             (1, None, 'orange bell pepper'),
    #             (1/4, 'teaspoon', 'black pepper'),
    #             (1, 'tablespoon', 'hot sauce'),
    #             (1, 'teaspoon', 'Worcestershire sauce')
    #         ])
    #     ]

    #     instructions = ('Chop the orange pepper. Grind the black pepper. '
    #         'Mix the Worcestershire. Add hot sauce to taste.')
    #     recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)
    #     self.assertEqual(len(recipe.graph), 4)  # 4 steps
    #     self.assertEqual(recipe.graph[0].ingredients, {ingredients[0]})
    #     self.assertEqual(recipe.graph[1].ingredients, {ingredients[1]})
    #     self.assertEqual(recipe.graph[2].ingredients, {ingredients[3]})
    #     self.assertEqual(recipe.graph[3].ingredients, {ingredients[2]})

    def test_match_multiple_ingredients(self):
        """Identify a reference to multiple ingredients,"""
        ingredients = [
            Ingredient(
                self.ureg.Quantity(magnitude, unit),
                name,
                i, 
                self.ureg, 
                self.nlp
            ) for i, (magnitude, unit, name) in enumerate([
                (2, 'cup', 'shredded cheddar cheese'),
                (1, 'cup', 'goat cheese'),
                (1, 'cup', 'parmesan cheese, shreddedef')
            ])
        ]
        instructions = ('Combine the cheeses in a large bowl.')
        recipe = Recipe(ingredients, instructions, self.ureg, self.nlp)
        self.assertEqual(len(recipe.graph), 1)  # 1 step
        self.assertEqual(recipe.graph[0].ingredients, set(ingredients))


        # if one match: use that
        # elif multiple matches:
        #     incorporate amod, compound words to narrow down
        # if still multiple matches:
        #     if matches are single and word is plural:
        #         use all matches


if __name__ == '__main__':
    unittest.main()
