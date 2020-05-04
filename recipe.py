import pint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


class Recipe:

    def __init__(self, ingredients: list, instructions: list, ureg: pint.UnitRegistry):
        self.ingredients = ingredients
        self.instructions = instructions
        self.ureg = ureg
        self.normalize_ingredients()

    def normalize_ingredients(self):
        total = self.ureg.Quantity(0, 'cup')
        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                total += ingr.quantity

        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                ingr.percent = (ingr.quantity.to('cup') / total).magnitude



    def plot_ingredients(self):
        fig_height = 6
        fig_width = 6

        panel_height = 5
        panel_width = 2


        height = panel_height / fig_height
        width = panel_width / fig_width

        plt.figure(figsize = (fig_width, fig_height))

        panel = plt.axes([0.1, 0.1, width, height])

        panel.set_xlim(0, 1)
        panel.set_ylim(0, 1)
        # turn off tick marks and labels
        panel.tick_params(
            bottom=False,
            labelbottom=False,
            left=False,
            labelleft=False
        )

        self.ingredients.sort(key=lambda x: x.percent, reverse=True)

        bottom = 0
        for i, ingr in enumerate(self.ingredients):
            rectangle = Rectangle(
                [0, bottom], 
                1,
                ingr.percent,
                edgecolor='black',
                facecolor=[
                    1 - (i / len(self.ingredients)),
                    1 - (i / len(self.ingredients)),
                    i / len(self.ingredients)
                ]
            )
            panel.add_patch(rectangle)
            bottom += ingr.percent

        plt.show()



    def print(self):
        for i in self.ingredients:
            print(i)

        for i in self.instructions:
            print(i)