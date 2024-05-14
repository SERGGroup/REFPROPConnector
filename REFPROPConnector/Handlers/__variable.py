from .Tools.units_converter import convert_variable, constants


class ThermodynamicVariable:

    def __init__(self, name: str):

        self.value = None
        self.name = name
        self.refprop_name = constants.get_refprop_name(name)
        self.is_user_defined = False
        self.order = 0

    @property
    def is_empty(self):
        return self.value is None

    def convert(self, rp_handler, to_unit_system):

        value, info = convert_variable(

            self.value, self.refprop_name,
            rp_handler.return_units(self.refprop_name),
            rp_handler.return_units(self.refprop_name, to_unit_system)

        )

        # TODO implement conversion mass / mole based system

        return value

    def set_from_different_us(self, value, rp_handler, from_unit_system):

        self.value, info = convert_variable(

            value, self.refprop_name,
            rp_handler.return_units(self.refprop_name, from_unit_system),
            rp_handler.return_units(self.refprop_name)

        )

    def __gt__(self, other):
        # enables comparison
        # self > other

        return self.order > other.order

    def __lt__(self, other):
        # enables comparison
        # self < other

        return self.order < other.order

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)
