import pint
import matplotlib.pyplot as plt
import numpy as np
import re
import spacy
from spacy import displacy

from container import Container
from node import Node
import spacy_helpers as sh



class Recipe:

    def __init__(self, ingredients, instructions, ureg, nlp):
        """
        Represent a recipe as a tree storing its ingedients and instructions

        Recipe is a directed graph of Nodes. The Recipe begins with one Node for
        each ingredient and no edges. For each step in the instructions, a Node
        is added as the child of the Node(s) being acted upon.

        For instance, if the recipe says 'mix the cheddar and parmesan', a Node
        is created that references the Ingredients that best match 'cheddar' and 
        'parmesan'. Edges point from the 'cheddar' Node and the 'parmesan' Node
        to the new 'cheddar and parmesan' Node.

        Parameters:
            ingredients: list of Ingredient objects representing all recipe ingredients
            instructions: string containing all the recipe instructions as sentences
            ureg: pint.UnitRegistry object, must be shared among all Ingredients
            nlp: spacy.Language object
        """


        self.ingredients = ingredients
        self.instructions = instructions
        self.ureg = ureg
        self.nlp = nlp

        self.normalize_ingredients()

        self.plot_ingredients()

        self.ingredient_nodes = []

        # The graph is a list of nodes, 
        # each one being the root of a different connected component.
        # It is updated as the graph grows and connects.
        # New Nodes may only be connected to Nodes that are in this list 
        # at the time they are instantiated.
        self.graph = self.initialize_graph()

        # This list of Nodes will store them in the order that they
        # are parsed/happen in the instructions
        self.order = []

        self.containers = []

        self.current_ref = None

        for sentence in self.nlp(instructions).sents:
            sent, = sentence.as_doc().sents
            self.parse_steps(sent)

        self.visualize()


    def initialize_graph(self) -> list:
        """Return a list of Nodes, one storing each Ingredient"""

        graph = []
        for i in self.ingredients:
            n = Node()
            n.ingredients.append(i)
            graph.append(n)
            self.ingredient_nodes.append(n)

        return graph


    def parse_steps(self, sent: spacy.tokens.Span):
        """
        Attempt to add a node joining ingredients for each recipe step

        Parameters:
            sent: spacy.Span object representing a recipe sentence
        """

        root = sent.root
        
        # Some steps have multiple clauses which should be treated as separate steps
        # Recursively parse any trailing clauses
        head, tail = sh.split_conjuncts(sent)

        #displacy.serve(head)

        # Most steps in recipes are commands
        # Ideally spacy will have identified the instruction verb as the sentence root
        if head.root.pos_ == 'VERB':

            action = head.root
            nouns = sh.get_all_nouns(sent)
            ingredient_nodes, containers = self.identify_objects(nouns)
     
            if ingredient_nodes:
                node = Node(action, ingredient_nodes)
                self.add_new_node(node)
            elif containers:
                self.current_ref = containers[0]
            else:
                if isinstance(self.current_ref, Node):
                    node = Node(action, [self.current_ref])
                    self.add_new_node(node) 


        else:
            head = list(self.nlp(head.text + '.').sents)[0]
            nouns = [n.root for n in head.noun_chunks]

            ingredient_nodes, containers = self.identify_objects(nouns)

            if ingredient_nodes:
                node = Node(head, ingredient_nodes)
                self.add_new_node(node)


        if tail:
                self.parse_steps(tail)

    def add_new_node(self, node: Node):
        """
        Insert a node into the graph

        Parameters:
            node: a Node to insert
        """
        self.graph.append(node)
        for parent in node.parents:
            try:
                self.graph.remove(parent)
            except:
                pass

        self.order.append(node)
        self.current_ref = node

    def visualize(self):
        """Display the recipe as a tree graph with matplotlib"""

        plt.figure(figsize = (8, 10))

        panel = plt.axes([0.1, 0.1, 0.7, 0.7], frameon=False)

        panel.set_xlim(-1, len(self.ingredients))
        panel.set_ylim(-1, len(self.order) + 1)

        # turn off tick marks and labels
        panel.tick_params(
            bottom=False,
            labelbottom=False,
            left=False,
            labelleft=False
        )

        # plot each ingredient as a node labeled with its name
        for i, ing in enumerate(self.ingredient_nodes):
            plt.plot(
                i,
                len(self.order),
                marker='o',
                markerfacecolor='green',
                markeredgewidth=0,
                markersize=8,
                linewidth=0,
            )
            plt.text(
                i,
                len(self.order),
                ' ' + ing.ingredients[0].name,
                verticalalignment='bottom',
                rotation=60
            )
            ing.x = i
            ing.y = len(self.order)

        # plot each recipe step as a node labeled with its action
        for i, node in enumerate(self.order):

            node.x = sum(p.x or 0 for p in node.parents) / len(node.parents)
            node.y = len(self.order) - 1 - i

            plt.plot(
                node.x,
                node.y,
                marker='o',
                markerfacecolor='green',
                markeredgewidth=0,
                markersize=8,
                linewidth=0,
            )

            plt.text(
                node.x,
                node.y,
                ' ' + node.action.text.split(' ')[0]
            )

            # plot lines connecting child nodes to parent nodes
            for parent in node.parents:
                plt.plot(
                    [parent.x, node.x],
                    [parent.y, node.y],
                    markersize=0,
                    linewidth=2
                )

        plt.show()



    def best_matching_node(self, token):

        scores = [node.max_base_similarity(token) for node in self.graph]
        if max(scores) >= 0.7:
            # return the node with the highest score
            match = self.graph[np.argmax(np.array(scores))]
            print(token, 'matches', match.ingredients)
        else:
            # if all the scores are low, the token likely isn't an ingredient
            print(token, 'matches nothing')
            return None


    def identify_objects(self, objs):

        ings, conts = [], []
        for obj in objs:
            identities = self.identify(obj)
            for identity in identities:
                if isinstance(identity, Node):
                    ings.append(identity)
                elif isinstance(identity, Container):
                    conts.append(identity)

        return ings, conts


    def identify(self, token) -> list:
        """
        Return the Node(s) to which the token refers

        Parameters:
            token: spacy Token representing the word to ID
        Returns:
            list of Nodes that the token may refer to
        """
        print(token.text)
        print('lemma:', token.lemma_)
        print([t.text for t in token.subtree])
        keyword = token.lemma_
        if self.is_kitchen_equipment(keyword):
            for container in self.containers:
                if keyword == container.name:
                    return [container]
            else:
                container = Container(keyword)
                self.add_new_container(container)
                return [container]

        else:
            matches = []
            for n in self.graph:
                for i in n.ingredients:
                    if i.has_words(keyword):
                        matches.append(n)
                        break
            if matches:
                return matches

            return [self.best_matching_node(token)] or []


    def add_new_container(self, container: Container):
        self.containers.append(container)

    def is_kitchen_equipment(self, word: str):
        kitchen_equipment = ['oven', 'pan', 'pot', 'bowl', 'dish', 'saucepan']
        if word in kitchen_equipment:
            return True
        return False


    def __str__(self):
        return self.text

    def normalize_ingredients(self):
        total = self.ureg.Quantity(0, 'cup')
        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                total += ingr.quantity

        for ingr in self.ingredients:
            if ingr.quantity.check('[volume]'):
                ingr.percent = (ingr.quantity.to('cup') / total).magnitude



    def plot_ingredients(self):
        """Display relative volumes of ingredients as a pie chart"""

        by_percent = sorted(self.ingredients, key=lambda x: x.percent, reverse=True)
        labels = [ingredient.name for ingredient in by_percent]
        sizes = [ingredient.percent for ingredient in by_percent]

        # make a unique rainbow color for each ingredient
        colors = plt.cm.rainbow(np.linspace(0, 1, len(by_percent)))

        plt.figure(figsize=(10, 5))
        
        panel = plt.axes([0.1, 0.1, 0.5, 0.8])

        panel.pie(sizes, colors=colors, radius=0.5)
        panel.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.legend(
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            labels=labels
        )

        plt.show()



    def print(self):
        for i in self.ingredients:
            print(i)

        for i in self.instructions:
            print(i)

