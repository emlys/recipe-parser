import pint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import spacy
from spacy import displacy


class Recipe:
    """Represent a recipe as a tree, where leaves are ingredients and the final product is the root"""

    def __init__(self, ingredients: list, instructions: list, ureg: pint.UnitRegistry, nlp):
        self.ingredients = ingredients
        self.instructions = instructions
        self.ureg = ureg
        self.nlp = nlp

        self.normalize_ingredients()

        self.graph = []

        self.current_node = None

        for i in ingredients:
            n = Node()
            n.ingredients.append(i)
            self.graph.append(n)

        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)


    def parse_steps(self, sent):

        print(sent)
        print(sent.root)
        root = sent.root
        #displacy.serve(sent, style='dep')
        
        if sent.root.pos_ == 'VERB':

            sent, tail = self.split_conjuncts(sent)

            if tail:
                self.parse_steps(tail)
                    

            dobjs = [child for child in sent.root.children if child.dep_ == 'dobj']
            print(dobjs)

            if len(dobjs) == 1:

                action = sent.root
                objects = dobjs[0].conjuncts
                print('objects:', objects)
                for o in objects:
                    self.identify(o)
                node = Node(action, objects)
                self.current_node = node

            elif len(dobjs) == 0:
                node = Node(sent.root, [self.current_node])
            else:
                print('too many dobjs!')

        else:
            print('not a verb')


    def get_conjuncts(self, token):
        return [child for child in token.children if child.dep_ == 'conj']

    def identify(self, obj):
        print(obj.text)

        # for i in self.ingredients:
        #     print(i.name, obj.similarity(i.span))

        sim = [obj.similarity(i.span) for i in self.ingredients]
        match = self.ingredients[np.argmax(np.array(sim))]
        print(match.name)
        return match

    def get_objects(self, token):

        

        head, tail = self.split_conjugates(token)
        objects = [head]

        while tail:
            
            head, tail = self.split_conjugates(tail)
            objects.append(head)

        return objects

    def split_conjuncts(self, span):

        print(span.root)
        # Get the first conjunct
        conjs = self.get_conjuncts(span.root)
        print(conjs)

        if conjs:
            conj = conjs[0]

            # Split around the coordinating conjunction, if there is one
            if conj.nbor(-1).dep_ == 'cc':
                head = span.doc[: conj.i - 1]
            else:
                 head = span.doc[: conj.i]

            tail = span.doc[conj.i :]

            return head, tail

        else:
            return span, None




    

    def __str__(self):
        return self.text







    def normalize_ingredients(self):
        total = self.ureg.Quantity(0, 'cup')
        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                total += ingr.quantity

        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                ingr.percent = (ingr.quantity.to('cup') / total).magnitude



    def plot_ingredients(self):
        """Display relative volumes of ingredients as a stacked bar graph"""

        plt.figure(figsize = (6, 6))

        panel = plt.axes([0.1, 0.1, 0.4, 0.8])
        panel.set_xlim(0, 1)
        panel.set_ylim(0, 1)

        # turn off tick marks and labels
        panel.tick_params(
            bottom=False,
            labelbottom=False,
            left=False,
            labelleft=False
        )

        # Sort so that the bars decrease in size as they go up
        self.ingredients.sort(key=lambda x: x.percent, reverse=True)

        # Plot a bar representing the relative volume each ingredient takes up
        bottom = 0
        for i, ingr in enumerate(self.ingredients):
            rectangle = Rectangle(
                [0, bottom], 
                1,
                ingr.percent,
                edgecolor='black',
                facecolor=[
                    1 - (i / len(self.ingredients)),
                    1 - (i / len(self.ingredients)),
                    i / len(self.ingredients)
                ]
            )
            panel.add_patch(rectangle)
            bottom += ingr.percent

        plt.show()



    def print(self):
        for i in self.ingredients:
            print(i)

        for i in self.instructions:
            print(i)


class Node:

    def __init__(self, action=None, children=None):

        self.action = action
        self.children = children or []
        self.parent = None
        self.ingredients = []

        for child in self.children:
            child.parent = self
            self.ingredients += child.ingredients


class Step:

    def __init__(self, action, objects):
        self.action = action
        self.objects = objects

        print(action.text, self.objects, "!")

    def get_matching_ingredients(self, sent):
        nouns = [token for token in sent if token.pos_ == 'NOUN']

        for noun in nouns:
            print(noun.text, end=' ')
            sims = [noun.similarity(i.base) for i in self.ingredients]
            
            if max(sims) < 0.65:
                print('not an ingredient')
            else:
                print(self.ingredients[np.argmax(np.array(sims))].name)




