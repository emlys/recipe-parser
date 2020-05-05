import pint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import spacy
from spacy import displacy

from container import Container
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

        self.ingredient_nodes = []

        # The graph is a list of nodes, 
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list 
        # at the time they are instantiated.
        self.graph = self.initialize_graph()

        # This list of Nodes will store them in the order that they
        # are parsed/happen in the instructions
        self.order = []

        self.containers = []

        self.current_ref = None

        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)

        self.visualize()


    def initialize_graph(self):
        """Return a list of Nodes, one storing each Ingredient"""

        graph = []
        for i in self.ingredients:
            n = Node()
            n.ingredients.append(i)
            graph.append(n)
            self.ingredient_nodes.append(n)

        return graph

    def parse_steps(self, sent):

        print(sent)
        print('current node:', self.current_ref)
        root = sent.root
        #displacy.serve(sent, style='dep')
        
        head, tail = self.split_conjuncts(sent)

        if head.root.pos_ == 'VERB':

            action = head.root
            dobjs = self.get_direct_objects(head.root)
            ingredient_nodes, containers = self.identify_objects(dobjs)
            print(ingredient_nodes)
            print(containers)
     
            if ingredient_nodes:
                node = Node(action, ingredient_nodes)
                print('just created node', node)
                self.add_new_node(node)
            elif containers:
                self.current_ref = containers[0]
            else:
                if isinstance(self.current_ref, Node):
                    node = Node(action, [self.current_ref])
                    print('just created node', node)
                    self.add_new_node(node)
                    

            

        else:
            print('not a verb')
            print(head.text)

            head = list(self.nlp(head.text + '.').sents)[0]
            nouns = [n.root for n in head.noun_chunks]
            print('nouns:', nouns)

            ingredient_nodes, containers = self.identify_objects(nouns)
            print('found', ingredient_nodes)
            print(containers)

            if ingredient_nodes:
                node = Node(head, ingredient_nodes)
                print('just created node', node)
                self.add_new_node(node)


        if tail:
                self.parse_steps(tail)

    def add_new_node(self, node):
        self.graph.append(node)
        for parent in node.parents:
            self.graph.remove(parent)

        self.order.append(node)
        self.current_ref = node

    def visualize(self):
        plt.figure(figsize = (8, 8))

        panel = plt.axes([0.1, 0.1, 0.7, 0.7])

        panel.set_xlim(-1, len(self.ingredients))
        panel.set_ylim(-1, len(self.order) + 1)

        # turn off tick marks and labels
        panel.tick_params(
            bottom=False,
            labelbottom=False,
            left=False,
            labelleft=False
        )

        for i, ing in enumerate(self.ingredient_nodes):
            plt.plot(
                i,
                len(self.order),
                marker='o',
                markerfacecolor='green',
                markeredgewidth=0,
                markersize=8,
                linewidth=0,
            )
            plt.text(
                i,
                len(self.order),
                ' ' + ing.ingredients[0].name,
                verticalalignment='bottom',
                rotation=60
            )
            ing.x = i
            ing.y = len(self.order)

        for i, node in enumerate(self.order):

            print('Node:', node, 'parents:', [p for p in node.parents])

            node.x = sum(p.x or 0 for p in node.parents) / len(node.parents)
            node.y = len(self.order) - 1 - i

            plt.plot(
                node.x,
                node.y,
                marker='o',
                markerfacecolor='green',
                markeredgewidth=0,
                markersize=8,
                linewidth=0,
            )

            plt.text(
                node.x,
                node.y,
                ' ' + node.action.text
            )

            for parent in node.parents:
                plt.plot(
                    [parent.x, node.x],
                    [parent.y, node.y],
                    markersize=0,
                    linewidth=2
                )



        plt.show()


    def get_conjuncts(self, token):
        """
        Return all child conjuncts of the token.
        This is different from the token.conjuncts attribute because this
        only includes conjuncts that are children of the token.
        """
        return [child for child in token.children if child.dep_ == 'conj']

    def get_direct_objects(self, token):
        """
        Return all direct objects of the token.
        """
        return [child for child in token.children if child.dep_ == 'dobj']

    def identify_objects(self, dobjs):

        if len(dobjs) == 0:
            return [], []
        else:
            objs = [d for d in dobjs]
            for d in dobjs:
                print(list(d.children))
                objs += self.get_conjuncts(d)

        ings, conts = [], []
        for obj in objs:
            identity = self.identify(obj)
            if isinstance(identity, Node):
                ings.append(identity)
            elif isinstance(identity, Container):
                conts.append(identity)
            else:
                print(type(identity))

        return ings, conts


    def identify(self, token):

        if self.is_kitchen_equipment(token):
            for container in self.containers:
                if token == container.name:
                    return container
            else:
                container = Container(token)
                self.add_new_container(container)
                return container

        else:
            return max(self.graph, key=lambda node: node.max_base_similarity(token))

    def add_new_container(self, container: Container):
        self.containers.append(container)

    def is_kitchen_equipment(self, token):
        kitchen_equipment = ['oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan']
        print('kitchen equipment?', token.text)
        if token.text in kitchen_equipment:
            return True
        return False


    def get_objects(self, token):
        
        head, tail = self.split_conjugates(token)
        objects = [head]

        while tail:
            
            head, tail = self.split_conjugates(tail)
            objects.append(head)

        return objects

    def split_conjuncts(self, span):
        # Get the first conjunct
        conjs = self.get_conjuncts(span.root)

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



