from .node import Node
from .ingredient import Ingredient


STEP_TYPE = 'step'


class Step(Node):

    def __init__(self, id_, span, verb_index, matches):
        """
        Instantiate a Step.
        Args:
            id_ (int): an identifier that's unique among all Nodes in the Recipe
            span (spacy.Span): the text of the step
            verb (int): index of token in self.span that's the main verb
            matches (list[Match]): a list of Match objects in this step.
        """
        super().__init__(id_)
        self.span = span
        self.verb_index = verb_index
        self.matches = matches

        self.parents = set([match.target_node for match in matches])
        self.ingredients = set()
        for parent in self.parents:
            print(type(parent))
            if type(parent) is Ingredient:
                self.ingredients.add(parent)
            else:
                self.ingredients = self.ingredients.union(parent.ingredients)

    def set_verb(self, token_index):
        """
        Mark a token of this Step as the main verb.
        Args:
            token_index (int): index of token to label in self.span
        Returns:
            None
        """
        self.verb = token_index

    def max_base_similarity(self, token) -> float:
        return max(token.similarity(i.base) for i in self.ingredients)

    def max_total_similarity(self, token) -> float:
        return max(token.similarity(i.span) for i in self.ingredients)

    def as_dict(self):
        """
        Return self represented as a dictionary.

        This is used in creating JSON web responses.
        """
        matched_indices = [
            word.i for match in self.matches for word in match.words]
        verb_child_phrases = []
        for token in self.span.doc[self.verb_index].children:
            if token.i not in matched_indices and not token.is_punct:
                verb_child_phrases.append(
                    [token.left_edge.i, token.right_edge.i])

        node_ids = []
        for match in self.matches:
            node_ids.append({
                'tokens': [word.i for word in match.words],
                'node_id': match.target_node.id,
                'type': match.type
            })

        return {
            'id': self.id,
            'type': STEP_TYPE,
            'ingredients': [ingredient.id for ingredient in self.ingredients],
            'parents': [parent.id for parent in self.parents],
            'start_index': self.span.start,
            'end_index': self.span.end - 1,
            'verb_index': self.verb_index,
            'node_ids': node_ids,
            'method': {self.verb_index: verb_child_phrases}
        }

    def __repr__(self):
        return f'<{self.span.text if self.span else None}>{self.ingredients}'
