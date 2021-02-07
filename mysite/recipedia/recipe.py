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
            n.ingredients.add(ingredient)
            self.ingredient_nodes.append(n)
        print(self.ingredient_nodes)
        self.current_ref = None

        self.node_index = len(self.ingredient_nodes)
        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)

        print(self.graph)

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

        # Most sentences in recipes are commands
        # Ideally spacy will have identified the imperative verb as the sentence root
        if self.is_imperative(head.root):

            step.set_verb(head.root.i)
            
            # direct objects: the dobj of the verb and its conjugates, if any
            dobjs = sh.get_direct_objects(head.root)
            # prepositional objects: verb --prep--> _ --pobj--> noun
            pobjs = sh.get_prepositional_objects(head.root)
            print(dobjs, pobjs)

            is_step = False
            all_matches = []

            # has dobj?   dobj matches?  has pobj?   pobj matches?
            #  yes           yes           yes           yes       use both
            #  yes           yes           yes           no        use dobj only
            #  yes           yes           no            --        use dobj only
            #  yes           no            yes           yes       (is this possible?)
            #  yes           no            yes           no        ignore this step
            #  yes           no            no            --        ignore this step
            #  no            --            yes           yes       use pobj; infer dobj is previous dobj
            #  no            --            yes           no        infer dobj is previous dobj (?)
            #  no            --            no            --        ignore this step
            #
            #  -> if the step has a prepositional object and no direct object, 
            #     infer that it's implicitly referring to the most recent dobj.

            for dobj in dobjs:
                matches = self.identify_object(dobj)
                if matches:
                    is_step = True
                    all_matches += matches

            for pobj in pobjs:
                matches = self.identify_object(pobj)
                if matches:
                    all_matches += matches
            
            # infer that it's implicitly referring to the stored reference
            if pobjs and not dobjs:
                print('inferring past ref')
                all_matches.append(Match([], None, self.current_ref))
                is_step = True

            print('all matches:', all_matches)
            if is_step:
                new_node = Node(
                    index=self.node_index, 
                    step=step,
                    matches=all_matches,
                    parents=[match.node for match in all_matches]
                )
                self.node_index += 1
                self.add_new_node(new_node)
                self.current_ref = new_node

            # otherwise, the object of the sentence isn't a node

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
        """Identify node(s) that the token refers to.

        Args:
            token (spacy.Token): token to identify
        Returns:
            list[Match]: a list of Match objects
        """

        print('token:', token)
        if token.text in {'oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan', 'foil'}:
            return []

        name = []
        max_index = token.i
        min_index = token.i
        for child in token.children:
            if child.dep_ == 'compound' or child.dep_ == 'amod':
                # a compound noun
                name.append(child)
                if child.i < min_index:
                    min_index = child.i

        name.append(token)

        matches = []
        max_count = 0
        print('name:', name)
        # Find the node(s) with the best matching ingredients
        # Determined by how many of the words in the reference are in the ingredient name
        for node in (self.ingredient_nodes + self.graph):
            for ingredient in node.ingredients:
                # compare by lemma
                # lemma is the root form of the word
                match_count = ingredient.num_matching_words([word.lemma_ for word in name])
                print(ingredient.name, match_count)
                if match_count > max_count:
                    matches = [Match(name, ingredient, node)]
                    max_count = match_count
                elif match_count == max_count:
                    matches.append(Match(name, ingredient, node))

        # make this return a list of matches
        print('matches:', matches)
        return matches

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


class Match:

    def __init__(self, words, target, node):
        """Initialize a match from words in the instructions to an ingredient.

        Args:
            words (list[token]): the tokens of an instruction step that match
            target (int): the ingredient index that the text matches
        """
        self.words = words
        self.target = target
        self.node = node

    def __repr__(self):
        return 'Match!' + ' '.join([word.text for word in self.words]) + ':' + str(self.target)





