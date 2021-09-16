import spacy
import sys
import unittest

sys.path.append('/Users/emily/recipe-parser/mysite/')
import recipedia.spacy_helpers as sh


class TestSpacyHelpers(unittest.TestCase):

    nlp = spacy.load('en_core_web_md')

    def test_get_prepositional_objects(self):
        span = self.nlp("Mix the milk with the cocoa powder.")[:]
        self.assertEqual(span.root.text, 'Mix')
        pobjs = sh.get_prepositional_objects(span.root)
        self.assertEqual(len(pobjs), 1)
        self.assertEqual(pobjs[0].text, 'powder')

        span = self.nlp("Fold the flour into the milk and eggs.")[:]
        self.assertEqual(span.root.text, 'Fold')
        pobjs = sh.get_prepositional_objects(span.root)
        self.assertEqual(len(pobjs), 2)
        self.assertEqual(pobjs[0].text, 'milk')
        self.assertEqual(pobjs[1].text, 'eggs')

        span = self.nlp("Pour into the pan of milk with a spoon.")[:]
        self.assertEqual(span.root.text, 'Pour')
        pobjs = sh.get_prepositional_objects(span.root)
        self.assertEqual(len(pobjs), 3)
        self.assertEqual(pobjs[0].text, 'pan')
        self.assertEqual(pobjs[1].text, 'milk')
        self.assertEqual(pobjs[2].text, 'spoon')



if __name__ == '__main__':
    unittest.main()