class Node:

    def __init__(self, index, instruction=None, action=None, parents=None):
        """
        Args:
            index (int): the index of this node in the recipe order
            instruction (spacy.Span): the sentence or clause corresponding to 
                this node
            action:
            parents (list[Node]): list of nodes that this node is derived from.
        """
        self.index = index
        self.instruction = instruction or ''
        self.action = action
        self.parents = parents or []
        self.children = []
        self.ingredients = []
        self.container = None
        self.x = None
        self.y = None

        for parent in self.parents:
            parent.children.append(self)
            self.ingredients += parent.ingredients

        if self.parents:
            self.container = self.parents[0].container


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
            'ingredients': [ingredient.name for ingredient in self.ingredients],
            'instruction': self.instruction.text if self.instruction else '',
            'parents': [parent.index for parent in self.parents]
        }

    def __repr__(self):
        return f'<{self.instruction}>{self.ingredients}'
