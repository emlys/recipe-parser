import requests
import re
from lxml import html
from bs4 import BeautifulSoup


class RecipeParser:

	def __init__(self):
		page = requests.get('https://www.momontimeout.com/best-homemade-baked-mac-and-cheese-recipe/')
		self.soup = BeautifulSoup(page.text, 'lxml')
		print(self.soup.title)
		self.ingredients = []

	def find_ingredients(self):
		# find list containers labeled with "ingredients"
		results = self.soup.find_all('ul', class_=lambda x: x is not None and 'ingredients' in x)

		for result in results:
			print('********\n\n')
			print(result)
			# find list items labeled with "ingredient"
			ingredients = result.find_all('li', class_=lambda x: x is not None and 'ingredient' in x)
			
			for ingredient in ingredients:
				self.parse_ingredient(ingredient.get_text())
			for i in self.ingredients:
				i.print()

	def parse_ingredient(self, string):
		# matches a three part ingredient in the format [quantity, unit, name]
		# where quantity is a number or fraction: 16, 1/3, and 1 1/2 all should match
		# unit is one word consisting of only alphabet characters
		# and name is the remainder of text on the line
		pattern = re.compile('([\d /]+) ([a-zA-Z]+) (.+)')
		match = pattern.match(string)

		if match:
			self.ingredients.append(Ingredient(match.group(1), match.group(2), match.group(3)))

		

class Ingredient:

	def __init__(self, quantity, unit, name):
		self.quantity = quantity
		self.unit = unit
		self.name = name

	def print(self):
		print(' | '.join([self.quantity, self.unit, self.name]))

if __name__ == '__main__':
	RecipeParser().find_ingredients()