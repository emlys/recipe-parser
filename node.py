class Node:

    def __init__(self, action=None, children=None):

        self.action = action
        self.children = children or []
        self.parent = None
        self.ingredients = []

        for child in self.children:
            child.parent = self
            self.ingredients += child.ingredients

        print(self.action, [i.name for i in self.ingredients], '!')


    def max_base_similarity(self, token) -> float:
        return max(token.similarity(i.base) for i in self.ingredients)

    def max_total_similarity(self, token) -> float:
        return max(token.similarity(i.span) for i in self.ingredients)

    def __repr__(self):
        ing_names = [i.name for i in self.ingredients]
        return '[ ' + ', '.join(ing_names) + ' ]'