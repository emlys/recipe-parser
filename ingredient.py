import pint


class Ingredient:

    def __init__(self, quantity, unit, name, notes, ureg):
        self.name = name
        self.notes = notes or ''
        self.ureg = ureg

        if quantity and unit:
            self.quantity = ureg.parse_expression(' '.join([quantity, unit]))
            #self.quantity, self.unit = q.magnitude, q.units
        else:
            self.quantity = pint.Quantity(0)

        self.percent = 0

    def __str__(self):
        return ' | '.join([str(self.quantity.magnitude), str(self.quantity.units), self.name, self.notes, str(self.percent)])