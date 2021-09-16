import recipy.scraper
import spacy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path')
args = parser.parse_args()

nlp = spacy.load('en_core_web_lg')
output_url_path = 'training_urls'


urls = []
with open(args.path) as f:
    for recipe_name in f:
        urls += recipy.scraper.scrape_google_search(
            recipe_name.strip() + ' recipe')

with open(output_url_path, 'w') as file:
    for url in urls:
        file.write(url + '\n')
