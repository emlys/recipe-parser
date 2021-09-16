import recipy.scraper
import spacy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path')
args = parser.parse_args()

nlp = spacy.load('en_core_web_lg')
output_sentence_path = 'training_sentences'

sentences = []
with open(args.path) as file:
    for url in file:
        result = recipy.scraper.scrape_recipe_url(url.strip())
        if result is None:
            continue
        doc = nlp(result[1])
        for sentence in doc.sents:
            sentences.append(sentence.text)

# with open(output_sentence_path, 'w') as file:
#     for sentence in sentences:
#         print(sentence)
#         file.write(sentence + '\n')
