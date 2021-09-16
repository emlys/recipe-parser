import numpy as np

from .step import Step
from . import spacy_helpers as sh


class RecipeParser:

    def __init__(self, ureg, nlp):
        self.ureg = ureg
        self.nlp = nlp

    def parse(self, ingredients, instructions, fulltext):
        # The graph is a list of nodes,
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list
        # at the time they are instantiated.
        graph = []

        document = self.nlp(instructions)
        # displacy.serve(self.document)

        node_id = len(ingredients)
        current_ref = None
        for clause in self.yield_clauses(document):
            step = self.parse_step(clause, node_id, current_ref)
            if step is not None:
                node_id += 1
                current_ref = step
                graph.append(step)

    def yield_clauses(self, doc):
        """Iterate through clauses in a document.

        Args:
            doc (spaCy.Document): document to iterate

        Yields: spacCy.Span s

        """
        def yield_clauses_from_sentence(sent):
            head, tail = sh.split_conjuncts(sent)
            yield head
            if tail:
                yield from yield_clauses_from_sentence(tail)

        for sentence in doc.sents:
            # Some steps have multiple clauses which should be treated as
            # separate steps. Recursively parse any trailing clauses
            yield from yield_clauses_from_sentence(sentence)

    def parse_step(self, clause, node_id, current_ref):
        """
        Parse a clause into a step node.

        Args:
            clause (spacy.Span): a complete recipe clause
            node_id (int): a unique ID to give the node

        Returns:
            Step node object
        """
        print('parsing clause:', clause)
        # Most sentences in recipes are commands
        # Ideally spacy will have identified the imperative verb as the sentence root
        all_matches = []
        if self.is_imperative(clause.root):

            # direct objects: the dobj of the verb and its conjugates, if any
            dobjs = sh.get_direct_objects(clause.root)
            # prepositional objects: verb --prep--> _ --pobj--> noun
            pobjs = sh.get_prepositional_objects(clause.root)
            print('dobjs:', dobjs)
            print('pobjs:', pobjs)

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
                for name, node in matches:
                    all_matches.append(Match(name, node, 'dobj'))

            for pobj in pobjs:
                matches = self.identify_object(pobj)
                for name, node in matches:
                    all_matches.append(Match(name, node, 'pobj'))

            # infer that it's implicitly referring to the stored reference
            if not dobjs:
                all_matches.append(Match([], current_ref, 'implicit'))
            print('matches:', all_matches)
            if all_matches:
                new_step = Step(
                    id_=node_id,
                    span=clause,
                    verb_index=clause.root.i,
                    matches=all_matches,
                )
                return new_step

        return None

    def is_imperative(self, token):
        """Check if a token is an imperative verb.
        It is imperative if the POS tag is the infinitive (VB) and
        the token has no subject.

        Args:
            token (spacy.Token): token to check
        Returns:
            boolean: True if imperative, False if not
        """
        print('is imperative?', token)
        print(token.tag_)
        print([child.dep_ == 'nsubj' for child in token.children])
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

        matches = []
        max_count = 0
        # Find the node(s) with the best matching ingredients
        # Determined by how many of the words in the reference are in the ingredient name
        for ingredient in self.ingredients:
            # compare by lemma
            # lemma is the root form of the word
            match_count = ingredient.num_matching_words(
                [word.lemma_.lower() for word in name])
            if match_count > max_count:
                matches = [(name, ingredient)]
                max_count = match_count
            elif match_count > 0 and match_count == max_count:
                matches.append((name, ingredient))

        for step in self.graph:
            for ingredient in step.ingredients:
                # compare by lemma
                # lemma is the root form of the word
                match_count = ingredient.num_matching_words(
                    [word.lemma_ for word in name])
                if match_count > max_count:
                    matches = [(name, step)]
                    max_count = match_count
                elif match_count > 0 and match_count == max_count:
                    matches.append((name, step))

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

    def __init__(self, words, target_node, match_type):
        """Initialize a match from words in the instructions to an ingredient.

        Args:
            words (list[token]): the tokens of an instruction step that match
            target_node (Node): the node (Step or Ingredient) that the text matches
            match_type (str): the type of match, one of 'dobj', 'pobj', or 'implicit'
        """
        # source type: dobj | pobj | implicit
        # target type: ingredient | output of previous step
        self.words = words
        self.target_node = target_node
        self.type = match_type

    def __repr__(self):
        return 'Match!' + ' '.join([word.text for word in self.words]) + ':' + str(self.target_node)
