import pint
import matplotlib.pyplot as plt
import numpy as np
import re
import spacy
from spacy import displacy

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

        # The graph is a list of nodes, 
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list 
        # at the time they are instantiated.
        self.graph = []

        self.ingredient_nodes = []
        for index, ingredient in enumerate(self.ingredients):
            n = Node(index)
            n.ingredients.add(index)
            self.ingredient_nodes.append(n)

        self.current_ref = None

        self.node_index = len(self.ingredient_nodes)
        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)


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
                    identity, (min_index, max_index) = self.identify_object(o)
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


    def identify(self, span):

        for obj in sh.get_objects(span.root):
            identity, (min_index, max_index) = self.identify_object(o)
        for pobj in sh.get_prepositional_objects(span.root)


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
            return None, (None, None)

        name = []
        max_index = token.i
        min_index = token.i
        for child in token.children:
            if child.dep_ == 'compound' or child.dep_ == 'amod':
                # a compound noun
                name.append(child.text)
                if child.i < min_index:
                    min_index = child.i

        name.append(token.text)
        name = ' '.join(name)

        matches = []
        for node in (self.ingredient_nodes + self.graph):
            for i in node.ingredients:
                if self.ingredients[i].has_words(name):
                    matches.append(node)
                    break
        print(name, 'matches:')
        for m in matches:
            print(m)
        if matches:
            return matches[0], (min_index, max_index)
        else:
            return None


    def add_new_node(self, node):
        """
        Insert a node into the graph

        Parameters:
            node: a Node to insert
        """
        print('adding new node')
        self.graph.append(node)
        self.current_ref = node



    def best_matching_node(self, token):

        scores = [node.max_base_similarity(token) for node in self.graph]
        if max(scores) >= 0.7:
            # return the node with the highest score
            match = self.graph[np.argmax(np.array(scores))]
        else:
            # if all the scores are low, the token likely isn't an ingredient
            return None


    def is_kitchen_equipment(self, word: str):
        kitchen_equipment = {'oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan'}
        if word in kitchen_equipment:
            return True
        return False


    def __str__(self):
        return self.text

