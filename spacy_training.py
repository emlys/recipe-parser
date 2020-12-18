import csv
import json
import pprint
import random
import spacy
from spacy.gold import docs_to_json

print('Loading spaCy...')
nlp = spacy.load("en_core_web_md")
print('done.')

full_sample_data_path = '/Users/emily/recipe-parser/full_sample_dataset.csv'
out_json_path = '/Users/emily/recipe-parser/training_data.json'

# read in all the sample data
full_sample_data = []
with open(full_sample_data_path) as data:
    reader = csv.DictReader(data)
    for row in reader:
        full_sample_data.append(row['instructions'])

# choose 50 random sentences from the sample data
sentence = random.choice(full_sample_data)
print(sentence)

# parse and tag it with spaCy
doc = nlp(sentence)
pp = pprint.PrettyPrinter()
doc_as_dict = docs_to_json(doc)
pp.pprint(doc_as_dict)

# append to file
with open(out_json_path, 'a', encoding='utf-8') as file:
    json.dump(doc_as_dict, file, ensure_ascii=False, indent=4)


spacy.displacy.serve(doc)