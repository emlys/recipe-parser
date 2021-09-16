

class Recipe:

    def __init__(self, ingredients, graph, orig_ingredients, orig_instructions, ureg, nlp):
        self.ingredients = ingredients
        self.graph = graph
        self.ureg = ureg
        self.nlp = nlp
