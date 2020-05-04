"""
Represent an instruction, or step of a recipe.
"""

import numpy as np
import ingredient
import spacy
from spacy import displacy


class Instructions:

    def __init__(self, doc, ingredients, nlp):

        self.doc = doc

        self.ingredients = ingredients
        self.nlp = nlp

        self.steps = self.parse_as_sentence(doc)

    
        

            #displacy.serve(sent, style='dep')
            #self.get_matching_ingredients(sent)


    def parse_as_sentence(self, doc):

        sentences = list(doc.sents)
        if len(sentences) > 1:
            steps = [self.parse_as_sentence(sent.as_doc()) for sent in sentences]
            return 

        sent = sentences[0]
        print(sent)
        print(sent.root)
        root = sent.root
        
        if sent.root.pos_ == 'VERB':

            if 'conj' in [child.dep_ for child in sent.root.children]:
                conj = [child for child in sent.root.children if child.dep_ == 'conj'][0]
                print(len(conj.doc), len(sent[0].doc), conj.i - 1)
                print(doc[conj.i])

                if doc[conj.i - 1].dep_ == 'cc':
                    i = conj.i - 1
                    j = conj.i
                else:
                    i = j = conj.i

                head = self.nlp(' '.join([n.text for n in sent[: i]]))
                tail = self.nlp(' '.join([n.text for n in sent[j :]]))

                return self.parse_as_sentence(head) + self.parse_as_sentence(tail)

            else:
                #displacy.serve(sent, style='dep')

                dobj = [child for child in sent.root.children if child.dep_ == 'dobj']

                if len(dobj) == 1:
                    return [Step(action=sent.root, obj=dobj[0])]
                elif len(dobj) == 0:
                    return [Step(action=sent.root, obj=None)]
                else:
                    print('too many dobjs!')



    def get_matching_ingredients(self, sent):
        nouns = [token for token in sent if token.pos_ == 'NOUN']

        for noun in nouns:
            print(noun.text, end=' ')
            sims = [noun.similarity(i.base) for i in self.ingredients]
            
            if max(sims) < 0.65:
                print('not an ingredient')
            else:
                print(self.ingredients[np.argmax(np.array(sims))].name)


    def __str__(self):
        return self.text


class Step:

    def __init__(self, action, obj):
        self.action = action
        self.object = obj

        if self.object:
            print(action.text + " " + obj.text + "!")
        else:
            print(action.text + "!")




