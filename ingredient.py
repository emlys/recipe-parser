import pint
import spacy


class Ingredient:

    def __init__(self, quantity, unit, name, notes, ureg, nlp):
        self.name = name
        self.notes = notes or ''
        self.ureg = ureg
        self.nlp = nlp


        if quantity and unit:
            self.quantity = ureg.parse_expression(' '.join([quantity, unit]))
        else:
            self.quantity = pint.Quantity(0)

        self.percent = 0

        self.span = list(self.nlp(self.name).sents)[0]

        for token in self.span:
                print(token, token.pos_, token.tag_, token.dep_)

        if self.span.root.pos_ == 'NOUN' or self.span.root.pos_ == 'PROPN':
            self.base = self.span.root
        else:
            for token in self.span:
                print(token.dep_)
            self.base = [token for token in self.span if token.dep_ == 'dobj'][0]

        print(self.name, self.base)
        



   


    def __str__(self):
        return ' | '.join([str(self.quantity.magnitude), str(self.quantity.units), self.name, self.notes, str(self.percent)])