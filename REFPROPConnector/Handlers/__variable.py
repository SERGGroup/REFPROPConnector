from .Tools.units_converter import convert_variable, constants


class ThermodynamicVariable:

    def __init__(self, name: str):

        self.value = None
        self.name = name

        self.__rel_uncertainty = None
        self.__abs_uncertainty = None

        self.refprop_name = constants.get_refprop_name(name)
        self.is_user_defined = False
        self.order = 0

    @property
    def rel_uncertainty(self):

        if self.__rel_uncertainty is not None:
            return self.__rel_uncertainty
        elif (self.value is not None and self.value != 0) and self.abs_uncertainty is not None:
            return self.abs_uncertainty / abs(self.value)
        return 0.0

    @rel_uncertainty.setter
    def rel_uncertainty(self, value):
        self.__rel_uncertainty = value

    @property
    def abs_uncertainty(self):

        if self.__abs_uncertainty is not None:
            return self.__abs_uncertainty
        elif (self.value is not None and self.value != 0) and self.rel_uncertainty is not None:
            return self.rel_uncertainty * abs(self.value)
        return  0.0

    @abs_uncertainty.setter
    def abs_uncertainty(self, value):
        self.__abs_uncertainty = value

    @property
    def is_empty(self):
        return self.value is None

    def convert(self, rp_handler, to_unit_system, value_to_convert=None):

        if value_to_convert is not None:
            value = value_to_convert
        else:
            value = self.value

        value, info = convert_variable(

            value, self.refprop_name,
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
