"""
Represents a thing in a recipe that is not an ingredient, and which can contain ingredients.
e.g. 'oven', 'a baking dish', 'the small mixing bowl' should be instantiated as Containers.
Locations and combinations of ingredients are defined in terms of their Containers.
"""
from node import Node


class Container:

    def __init__(self, name):
        self.name = name
                