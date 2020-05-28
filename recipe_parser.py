import argparse
import pint
import re
import requests
import spacy

from bs4 import BeautifulSoup

from ingredient import Ingredient
from recipe import Recipe


class RecipeParser:

	def __init__(self):
		print('Loading spacy package...')
		self.nlp = spacy.load('en_core_web_lg')
		print('Loading pint unit registry...')
		self.ureg = pint.UnitRegistry()

	def parse(self, url: str):
		"""Try to parse the webpage as a WordPress recipe"""
		print("Parsing recipe...")
		page = requests.get(url)
		self.soup = BeautifulSoup(page.text, 'lxml')

		if self.is_wordpress_recipe(self.soup):
			self.parse_wordpress_recipe(self.soup)
		else:
			print('Recipe is not in WordPress Recipe Maker format')

	def is_wordpress_recipe(self, soup: BeautifulSoup):
		"""Return True if soup contains a WordPress recipe"""
		ingr = 'wprm-recipe-ingredients-container'
		inst = 'wprm-recipe-instructions-container'
		if self.soup.find(class_=ingr) and self.soup.find(class_=inst):
			return True
		return False

	def parse_wordpress_recipe(self, soup: BeautifulSoup):
		"""Read and interpret ingredients and instructions from a WordPress recipe"""
		ingredient_tags = self.soup.find_all('li', class_='wprm-recipe-ingredient')
		instruction_tags = self.soup.find_all('div', class_='wprm-recipe-instruction-text')

		ingredients, instructions = [], []

		for tag in ingredient_tags:
			amount = tag.find('span', class_='wprm-recipe-ingredient-amount')
			unit = tag.find('span', class_='wprm-recipe-ingredient-unit')
			name = tag.find('span', class_='wprm-recipe-ingredient-name')
			notes = tag.find('span', class_='wprm-recipe-ingredient-notes')

			amount, unit, name, notes = [attr.get_text().lower() if attr else None for attr in [amount, unit, name, notes]]

			ingredients.append(Ingredient(amount, unit, name, notes, self.ureg, self.nlp))

		instructions = ' '.join([tag.get_text() for tag in instruction_tags])

		r = Recipe(ingredients, instructions, self.ureg, self.nlp)

		return r


def main():
	"""Entrypoint for recipe parser"""

	# parse command line args
	parser = argparse.ArgumentParser()
	parser.add_argument('url', help='URL of recipe to parse')
	args = parser.parse_args()

	RecipeParser().parse(args.url)


if __name__ == '__main__':
	main()
	


