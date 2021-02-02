class Node:

    def __init__(self, index, step=None, parents=None):
        """
        Args:
            index (int): the index of this node in the recipe order
            step (Step): the sentence or clause corresponding to 
                this node
            action:
            parents (list[Node]): list of nodes that this node is derived from.
        """
        self.index = index
        self.step = step
        self.parents = parents or []
        # a set of ints pointing to index of Recipe.ingredients
        self.ingredients = set()  

        for parent in self.parents:
            self.ingredients = self.ingredients.union(parent.ingredients)

    def max_base_similarity(self, token) -> float:
        return max(token.similarity(i.base) for i in self.ingredients)

    def max_total_similarity(self, token) -> float:
        return max(token.similarity(i.span) for i in self.ingredients)

    def as_dict(self) :
        """Return self represented as a dictionary.

        This is used in creating JSON web responses.
        """
        return {
            'name': self.index, 
            'ingredients': self.ingredients,
            'step': self.step.as_dict() if self.step else None,
            'parents': [parent.index for parent in self.parents]
        }

    def __repr__(self):
        return f'<{self.step.span.text if self.step else None}>{self.ingredients}'
