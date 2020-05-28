class Node:

    def __init__(self, action=None, parents=None):

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

    # def __repr__(self):
    #     ing_names = ','.join([i.name for i in self.ingredients])
    #     cont_name = self.container.name.text if self.container else 'none'
    #     action_name = self.action.text if self.action else 'none'
    #     return 'Node{\n\taction: ' + action_name + '\n\tingredients:' + ing_names + '\n\tcontainer:' + cont_name + '\n}'