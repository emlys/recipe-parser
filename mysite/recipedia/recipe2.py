import pint
import numpy as np
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

        # The graph is a list of nodes,
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list
        # at the time they are instantiated.
        self.graph = []

        self.document = self.nlp(instructions)

        node_id = len(ingredients)
        current_ref = None
        for clause in self.yield_clauses(self.document):
            step = self.parse_step(clause, node_id, current_ref)
            node_id += 1
            current_ref = step
            self.graph.append(step)

        print(self.graph)

    def yield_clauses(self, doc):
        """Iterate through clauses in a document.

        Args:
            doc (spaCy.Document): document to iterate

        Yields: spacCy.Span s

        """
        def yield_clauses_from_sentence(sent):
            head, tail = sh.split_conjuncts2(sentence)
            yield head
            if tail:
                yield_clauses_from_sentence(tail)

        for sentence in doc.sents:
            # Some steps have multiple clauses which should be treated as
            # separate steps. Recursively parse any trailing clauses
            for clause in yield_clauses_from_sentence(sentence):
                yield clause

    def parse_step(self, clause, node_id, current_ref):
        """
        Parse a clause into a step node.

        Args:
            clause (spacy.Span): a complete recipe clause
            node_id (int): a unique ID to give the node

        Returns:
            Step node object
        """
        # Most sentences in recipes are commands
        # Ideally spacy will have identified the imperative verb as the sentence root
        all_matches = []
        if self.is_imperative(clause.root):

            # direct objects: the dobj of the verb and its conjugates, if any
            dobjs = sh.get_direct_objects(clause.root)
            # prepositional objects: verb --prep--> _ --pobj--> noun
            pobjs = sh.get_prepositional_objects(clause.root)
            print(dobjs, pobjs)

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
                    all_matches += matches

            for pobj in pobjs:
                matches = self.identify_object(pobj)
                if matches:
                    all_matches += matches

            # infer that it's implicitly referring to the stored reference
            if pobjs and not dobjs:
                all_matches.append(Match([], current_ref))

        new_step = Step(
            id_=node_id,
            span=clause,
            verb_index=clause.root.i,
            matches=all_matches,
        )
        return new_step

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

        non_foods = set()
        with open('/Users/emily/recipe-parser/mysite/recipedia/not_a_food.txt') as file:
            for line in file:
                non_foods.add(line.strip())

        if token.text in non_foods:
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
        print('identify', token)

        matches = []
        max_count = 0
        # Find the node(s) with the best matching ingredients
        # Determined by how many of the words in the reference are in the ingredient name
        for ingredient in self.ingredients:
            # compare by lemma
            # lemma is the root form of the word
            match_count = ingredient.num_matching_words([word.lemma_.lower() for word in name])
            print(ingredient.name, match_count)
            if match_count > max_count:
                matches = [Match(name, ingredient)]
                max_count = match_count
            elif match_count > 0 and match_count == max_count:
                matches.append(Match(name, ingredient))

        for step in self.graph:
            for ingredient in step.ingredients:
                # compare by lemma
                # lemma is the root form of the word
                match_count = ingredient.num_matching_words([word.lemma_ for word in name])
                if match_count > max_count:
                    matches = [Match(name, step)]
                    max_count = match_count
                elif match_count > 0 and match_count == max_count:
                    matches.append(Match(name, step))

        # make this return a list of matches
        return matches

    def best_matching_node(self, token):

        scores = [node.max_base_similarity(token) for node in self.graph]
        if max(scores) >= 0.7:
            # return the node with the highest score
            match = self.graph[np.argmax(np.array(scores))]
        else:
            # if all the scores are low, the token likely isn't an ingredient
            return None

    def __str__(self):
        return self.text


class Match:

    def __init__(self, words, target_node):
        """Initialize a match from words in the instructions to an ingredient.

        Args:
            words (list[token]): the tokens of an instruction step that match
            target_node: the node (Step or Ingredient) that the text matches
        """
        self.words = words
        self.target_node = target_node

    def __repr__(self):
        return 'Match!' + ' '.join([word.text for word in self.words]) + ':' + str(self.target_node)


class SingleSet(set):
    """A set that complains if you try to add an item that's already in it."""
    def add(self, value):
        if value in self:
            raise ValueError(f'Value {value} already in this set!')
        super().add(value)  # call the parent class add method



