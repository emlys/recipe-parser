from .node import Node
from .ingredient import Ingredient


class Step(Node):

    def __init__(self, id_, span, verb_index, matches):
        """Instantiate a Step.
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
        """Mark a token of this Step as the main verb.
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

    def as_dict(self) :
        """Return self represented as a dictionary.

        This is used in creating JSON web responses.
        """
        return {
            'ingredients': [ingredient.id for ingredient in self.ingredients],
            'parents': [parent.id for parent in self.parents],
            'tokens': {token.i: token.text for token in self.span},
            'verb_index': self.verb_index,
            'labels': {
                match.target_node.id: [word.i for word in match.words] 
                    for match in self.matches
            },
            'full_text': self.span.text
        }

    def __repr__(self):
        return f'<{self.span.text if self.span else None}>{self.ingredients}'


