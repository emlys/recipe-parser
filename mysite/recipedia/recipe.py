import pint
import matplotlib.pyplot as plt
import numpy as np
import re
import spacy
from spacy import displacy

from .container import Container
from .node import Node
from .step import Step
from . import spacy_helpers as sh



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

        Parameters:
            ingredients: list of Ingredient objects representing all recipe ingredients
            instructions: string containing all the recipe instructions as sentences
            ureg: pint.UnitRegistry object, must be shared among all Ingredients
            nlp: spacy.Language object
        """


        self.ingredients = ingredients
        self.instructions = instructions
        self.ureg = ureg
        self.nlp = nlp

        print(self.ingredients)

        self.ingredient_nodes = []

        # This list of Nodes will store them in the order that they
        # are parsed/happen in the instructions
        self.order = []

        # The graph is a list of nodes, 
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list 
        # at the time they are instantiated.
        self.graph = []
        for index, ingredient in enumerate(self.ingredients):
            n = Node(index)
            n.ingredients.append(index)
            self.graph.append(n)
            self.order.append(n)
            self.ingredient_nodes.append(n)

        self.graph_surface = self.graph.copy()

        self.containers = []

        self.current_ref = None

        self.node_index = len(self.ingredient_nodes)
        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)

        print(self.order)
        for node in self.order:
            if node.step:
                print(node.step.span.text)
                if node.step.verb:
                    print('verb:', node.step.verb)
                    print(node.step.span.doc[node.step.verb])
                for key, val in node.step.labels.items():
                    print('key, val:', key, val)
                    print('ingredient:', node.step.span[key], self.order[val])


    def parse_steps(self, sent):
        """
        Attempt to add a node joining ingredients for each recipe step

        Parameters:
            sent: spacy.Span object representing a recipe sentence
        """

        root = sent.root
        
        # Some steps have multiple clauses which should be treated as separate steps
        # Recursively parse any trailing clauses
        head, tail = sh.split_conjuncts(sent)
        print('start:', head.start)
        for word in head:
            print(word)
        #displacy.serve(head)

        step = Step(head)

        # Most steps in recipes are commands
        # Ideally spacy will have identified the imperative verb as the sentence root
        if self.is_imperative(head.root):

            step.set_verb(head.root.i)
            
            objs = sh.get_objects(head.root)
            print('head:', head, head.root, head.root.i)
            if objs:
                nodes = []
                for o in objs:
                    identity = self.identify_object(o)
                    if identity:
                        nodes.append(identity)
                        print(o, o.i, 'matches', identity, identity.index)
                        step.label_item(o.i, identity.index)

                if nodes:
                    new_node = Node(
                        index=self.node_index, 
                        step=step,
                        parents=nodes
                    )
                    self.node_index += 1
                    self.add_new_node(new_node)
                    self.current_ref = new_node

                # otherwise, the object of the sentence isn't a node

            else:
                if isinstance(self.current_ref, Node):
                    new_node = Node(
                        index=self.node_index, 
                        step=step,
                        parents=[self.current_ref]
                    )
                    self.node_index += 1
                    self.add_new_node(new_node) 

        else:
            pass


        if tail:
                self.parse_steps(tail)


    def is_imperative(self, token):
        """Check if a token is an imperative verb.
        It is imperative if the POS tag is the infinitive (VB) and
        the token has no subject.

        Args:
            token (spacy.Token): token to check
        Returns:
            boolean: True if imperative, False if not
        """
        if (token.tag_ == 'VB' and 
                sum([child.dep_ == 'nsubj' for child in token.children]) == 0):
            return True
        return False

    def identify_object(self, token):

        print('token:', token)
        if token.text in {'oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan', 'foil'}:
            return None

        name = []
        for child in token.children:
            if child.dep_ == 'compound' or child.dep_ == 'amod':
                # a compound noun
                name.append(child.text)

        name.append(token.text)
        name = ' '.join(name)

        matches = []
        for node in self.graph_surface:
            for i in node.ingredients:
                if self.ingredients[i].has_words(name):
                    matches.append(node)
                    break
        print(name, 'matches:')
        for m in matches:
            print(m)
        if matches:
            return matches[0]
        else:
            return None




    def add_new_node(self, node):
        """
        Insert a node into the graph

        Parameters:
            node: a Node to insert
        """
        self.graph.append(node)
        self.graph_surface.append(node)
        for parent in node.parents:
            try:
                self.graph_surface.remove(parent)
            except:
                pass

        self.order.append(node)
        self.current_ref = node



    def best_matching_node(self, token):

        scores = [node.max_base_similarity(token) for node in self.graph_surface]
        if max(scores) >= 0.7:
            # return the node with the highest score
            match = self.graph_surface[np.argmax(np.array(scores))]
        else:
            # if all the scores are low, the token likely isn't an ingredient
            return None


    def identify_objects(self, objs):

        ings, conts = [], []
        for obj in objs:
            identities = self.identify(obj)
            for identity in identities:
                if isinstance(identity, Node):
                    ings.append(identity)
                elif isinstance(identity, Container):
                    conts.append(identity)

        return ings, conts


    def identify(self, token) -> list:
        """
        Return the Node(s) to which the token refers

        Parameters:
            token: spacy Token representing the word to ID
        Returns:
            list of Nodes that the token may refer to
        """
        keyword = token.lemma_
        if self.is_kitchen_equipment(keyword):
            for container in self.containers:
                if keyword == container.name:
                    return [container]
            else:
                container = Container(keyword)
                self.add_new_container(container)
                return [container]

        else:
            matches = []
            for n in self.graph_surface:
                for i in n.ingredients:
                    if i.has_words(keyword):
                        matches.append(n)
                        break
            if matches:
                return matches

            return [self.best_matching_node(token)] or []


    def add_new_container(self, container: Container):
        self.containers.append(container)

    def is_kitchen_equipment(self, word: str):
        kitchen_equipment = {'oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan'}
        if word in kitchen_equipment:
            return True
        return False


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
        """Display relative volumes of ingredients as a pie chart"""

        by_percent = sorted(self.ingredients, key=lambda x: x.percent, reverse=True)
        labels = [ingredient.name for ingredient in by_percent]
        sizes = [ingredient.percent for ingredient in by_percent]

        # make a unique rainbow color for each ingredient
        colors = plt.cm.rainbow(np.linspace(0, 1, len(by_percent)))

        plt.figure(figsize=(10, 5))
        
        panel = plt.axes([0.1, 0.1, 0.5, 0.8])

        panel.pie(sizes, colors=colors, radius=0.5)
        panel.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.legend(
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            labels=labels
        )

        plt.show()



    def print(self):
        for i in self.ingredients:
            print(i)

        for i in self.instructions:
            print(i)

