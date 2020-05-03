import pint
import re
import requests
from bs4 import BeautifulSoup
from fractions import Fraction
from lxml import html

from ingredient import Ingredient
from instruction import Instruction
from recipe import Recipe


class RecipeParser:

	def __init__(self, url, ureg):
		page = requests.get(url)
		self.soup = BeautifulSoup(page.text, 'lxml')
		self.ureg = ureg

	def is_wordpress_recipe(self):
		if self.soup.find('wprm-recipe-ingredients-container') and self.soup.find('wprm-recipe-instructions-container'):
			return True
		return False

	def parse_wordpress_recipe(self):
		ingredient_tags = self.soup.find_all('li', class_='wprm-recipe-ingredient')
		instruction_tags = self.soup.find_all('li', class_='wprm-recipe-instruction')

		ingredients, instructions = [], []

		for i in ingredient_tags:
			amount = i.find('span', class_='wprm-recipe-ingredient-amount')
			unit = i.find('span', class_='wprm-recipe-ingredient-unit')
			name = i.find('span', class_='wprm-recipe-ingredient-name')
			notes = i.find('span', class_='wprm-recipe-ingredient-notes')

			amount, unit, name, notes = [attr.get_text() if attr else None for attr in [amount, unit, name, notes]]

			ingredients.append(Ingredient(amount, unit, name, notes, self.ureg))

		for i in instruction_tags:
			text = i.find('div', class_='wprm-recipe-instruction-text').get_text()
			instructions.append(Instruction(text))

		r = Recipe(ingredients, instructions, self.ureg)
		r.print()
		r.plot_ingredients()
		return r


	# def find_ingredients(self):
	# 	# find list containers labeled with "ingredients"
	# 	results = self.soup.find_all('ul', class_=lambda x: x is not None and 'ingredients' in x)

	# 	for result in results:
			
	# 		# find list items labeled with "ingredient"
	# 		list_items = result.find_all('li', class_=lambda x: x is not None and 'ingredient' in x)
			
	# 		return [self.parse_ingredient(li.get_text()) for li in list_items]


	# def parse_ingredient(self, string):
	# 	name, qualifier, quantity, unit = None, '', None, None

	# 	# matches a three part ingredient in the format [quantity, unit, name]
	# 	# where quantity is a number or fraction: '16', '1/3', '1.5', and '1 1/2' all should match
	# 	# unit is one word consisting of only alphabet characters
	# 	# and name is the remainder of text on the line
	# 	ingr = re.compile(r'([\d /\.]+) ([a-zA-Z]+) (.+)').match(string)

	# 	if ingr:  # ideally there will be a quantity and unit listed with the ingredient
	# 		quantity, unit, name = ingr.group(1), ingr.group(2), ingr.group(3)
	# 	else:     # but sometimes there's not, like 'salt and pepper to taste'
	# 		name = string

	# 	# check if the ingredient name contains a qualifying description contained in parentheses,
	# 	# such as 'smoked paprika (or regular paprika)'
	# 	# and store the qualifier separately from the ingredient name
	# 	# TODO expand this to recognize adjectives and comma-separated descriptions
	# 	qual = re.compile(r'(.+)(\(.+\))').match(name)  # >=1 chars followed by >=1 chars within parentheses
	# 	if qual:
	# 		name, qualifier = qual.group(1), qual.group(2)

	# 	return Ingredient(quantity, unit, name, qualifier, self.ureg)






if __name__ == '__main__':
	r = RecipeParser('https://www.momontimeout.com/best-homemade-baked-mac-and-cheese-recipe/', pint.UnitRegistry())
	print(r.is_wordpress_recipe())
	r.parse_wordpress_recipe()


