import pint
import spacy


class Recipy:

    def __init__(self):
        """Instantiate NLP package and unit registry to use in Recipes"""
        print('Loading spacy package...')
        self.nlp = spacy.load('en_core_web_md')  # this takes a couple seconds
        print('done.')
        self.ureg = pint.UnitRegistry()
