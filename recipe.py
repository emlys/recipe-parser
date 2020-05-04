import pint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import spacy
from spacy import displacy

from node import Node


class Recipe:

    def __init__(self, ingredients, instructions, ureg, nlp):
        """
        Represent a recipe as a tree storing its ingedients and instructions

        Recipe is a directed graph of Nodes. The Recipe begins with one Node for
        each ingredient and no edges. For each step in the instructions, a Node
        is added as the child of the Node(s) being acted upon.

        For instance, if the recipe says 'mix the cheddar and parmesan', a Node
        is created that references the Ingredients that best match 'cheddar' and 
        'parmesan'. Edges point from the 'cheddar' Node and the 'parmesan' Node
        to the new 'cheddar and parmesan' Node.

        ingredients: list of Ingredient objects representing all recipe ingredients
        instructions: string containing all the recipe instructions as sentences
        ureg: pint.UnitRegistry object, must be shared among all Ingredients
        nlp: spacy.Language object
        """


        self.ingredients = ingredients
        self.instructions = instructions
        self.ureg = ureg
        self.nlp = nlp

        self.normalize_ingredients()

        # The graph is a list of nodes, 
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list 
        # at the time they are instantiated.
        self.graph = self.initialize_graph()

        self.current_node = None

        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)

    def initialize_graph(self):
        """Return a list of Nodes, one storing each Ingredient"""

        graph = []
        for i in self.ingredients:
            n = Node()
            n.ingredients.append(i)
            graph.append(n)

        return graph

    def parse_steps(self, sent):

        print(sent)
        print(sent.root)
        print('current node:', self.current_node.ingredients if self.current_node else None)
        root = sent.root
        #displacy.serve(sent, style='dep')
        
        head, tail = self.split_conjuncts(sent)

        if head.root.pos_ == 'VERB':

            action = head.root
            objects = self.identify_objects(head.root)
            print('objects:', objects)
     
            node = Node(action, objects)
            self.current_node = node

        else:
            print('not a verb')


        if tail:
                self.parse_steps(tail)


    def get_conjuncts(self, token):
        """
        Return all child conjuncts of the token.
        This is different from the token.conjuncts attribute because this
        only includes conjuncts that are children of the token.
        """
        print("get conjuncts")
        return [child for child in token.children if child.dep_ == 'conj']

    def get_direct_objects(self, token):
        """
        Return all direct objects of the token.
        """
        print("get direct objects")
        return [child for child in token.children if child.dep_ == 'dobj']

    def identify_objects(self, token):
        print("identify objects")
        dobjs = self.get_direct_objects(token)
        print('direct objects:', dobjs)

        if len(dobjs) == 0:
            return []
        else:
            objs = [d for d in dobjs]
            for d in dobjs:
                objs += self.get_conjuncts(d)

        print(objs)
        ids = [self.identify(obj) or Container(obj) for obj in objs]

        return ids




    def identify(self, token):
        print("identify", token)
        print(self.graph)
        print([node.max_base_similarity(token) for node in self.graph])
        return max(self.graph, key=lambda node: node.max_base_similarity(token))


    def get_objects(self, token):
        print("get objects")
        

        head, tail = self.split_conjugates(token)
        objects = [head]

        while tail:
            
            head, tail = self.split_conjugates(tail)
            objects.append(head)

        return objects

    def split_conjuncts(self, span):
        print("splitting conjuncts")

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



