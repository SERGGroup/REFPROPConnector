import warnings
from CoolProp.CoolProp import PropsSI

from . import ThermodynamicVariable
from .__base_handler import BaseHandler, DEFAULT_UNIT_SYSTEM


class CoolpropHandler(BaseHandler):

    def new_evaluate_dll(self, str_out: str, variable_a: ThermodynamicVariable, variable_b: ThermodynamicVariable):
        pass

    @classmethod
    def coolprop_fluid_name(cls, fluids: list, composition: list):

        if len(fluids) == 1:
            return fluids[0]

        cp_name = "HEOS::{fluid}[{comp}]".format(fluid=fluids[0], comp=composition[0])

        for i in range(len(fluids) - 1):
            cp_name += "&{fluid}[{comp}]".format(fluid=fluids[i + 1], comp=composition[i + 1])

        return cp_name

    def __init__(self, fluids: list, composition: list, unit_system="SI WITH C"):

        self.fluid_name = self.coolprop_fluid_name(fluids, composition)
        super().__init__(fluids, composition, unit_system)

    def evaluate_dll(self, str_in: str, str_out: str, a: float, b: float):

        return PropsSI('T','P',101325,'Q',0,'Water')

    def set_unit_system(self, unit_system_input):

        self.__unit_system = unit_system_input

        try:

            self.SI = self.refprop.GETENUMdll(0, self.__unit_system).iEnum

        except:

            self.SI = self.refprop.GETENUMdll(0, DEFAULT_UNIT_SYSTEM).iEnum

            warning_message = (

                """
                    {} unit system is not supported,
                    {} has been used instead\n
                    Check in the REFPROP manual for the correct
                    name of the system that you wanted to use
                """

            ).format(self.__unit_system, DEFAULT_UNIT_SYSTEM)

            warnings.warn(warning_message)
            self.__unit_system = DEFAULT_UNIT_SYSTEM
