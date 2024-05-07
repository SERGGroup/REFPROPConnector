from .__variable import ThermodynamicVariable, convert_variable, constants
from .__quality_iteration import CODES_TO_BE_ITERATED, QualityIteration
from abc import ABC, abstractmethod
import warnings


GLOBALCounter = 0
ACTIVE_HANDLERS = []
HANDLER_SUBCLASSES = {}
DEFAULT_UNIT_SYSTEM = "SI WITH C"


class BaseHandler(ABC):

    T_0 = 0.
    TC = 0.
    T_trip = 0.

    P_0 = 0.
    PC = 0.
    P_trip = 0.

    H_0 = 0.
    S_0 = 0.

    __unit_system = DEFAULT_UNIT_SYSTEM

    def __init__(self, fluids: list, composition: list, unit_system=DEFAULT_UNIT_SYSTEM):

        # If REFPROP is available the program uses it, otherwise COOLPROP is used

        #   DEFAULT MEASURE UNITS:
        #
        #   Temperature:        [°C]
        #   Pressure:           [MPa]
        #   Density:            [kg/m^3]
        #   Enthalpy:           [kJ/kg]
        #   Entropy:            [kJ/(kg*K)]
        #   Speed:              [m/s]
        #   Kinematic vis.:     [cm^2/s]
        #   Viscosity:          [uPa*s]
        #   Thermal cond.:      [mW/(m*K)]
        #   Surface tension:    [mN/m]
        #   Molar Mass:         [kg/kmol]
        #   Heat Capacity:      [kJ/(kg*K)]

        self.fluids = fluids
        self.composition = composition
        self.unit_system = unit_system

    def set_reference_state(self, T_0=20, P_0=101325, T_0unit="C", P_0unit="Pa", old_unit_system=None):

        T_unit = self.return_units("T")
        P_unit = self.return_units("P")

        if old_unit_system is not None:

            T_unit_old = self.return_units("T", unit_system=old_unit_system)
            P_unit_old = self.return_units("P", unit_system=old_unit_system)

            self.T_0, info = convert_variable(self.T_0, "T",  T_unit_old, T_unit)
            self.P_0, info = convert_variable(self.P_0, "p",  P_unit_old, P_unit)

        else:

            self.T_0, info = convert_variable(T_0, "T", T_0unit, T_unit)
            self.P_0, info = convert_variable(P_0, "p", P_0unit, P_unit)

        self.H_0 = self.base_calculate("TP", "H", self.T_0, self.P_0)
        self.S_0 = self.base_calculate("TP", "s", self.T_0, self.P_0)

    def base_calculate(self, str_in: str, str_out: str, a: float, b: float):

        global GLOBALCounter

        if str_in in CODES_TO_BE_ITERATED:

            qi = QualityIteration(self, str_in, str_out, a, b)
            return qi.result

        if str_out == "Q":

            if self.unit_is_mass_based:

                str_out = "QMASS"

            else:

                str_out = "QMOLE"

        GLOBALCounter += 1
        return self.base_evaluate_dll(str_in, str_out, a, b)

    def calculate(self, str_out: str, variable_a: ThermodynamicVariable, variable_b: ThermodynamicVariable, metastb=""):

        global GLOBALCounter
        GLOBALCounter += 1

        return self.evaluate_dll(str_out, variable_a, variable_b, metastb)

    @abstractmethod
    def evaluate_dll(self, str_out: str, variable_a: ThermodynamicVariable, variable_b: ThermodynamicVariable, metastb=""):
        pass

    @abstractmethod
    def base_evaluate_dll(self, str_in: str, str_out: str, a: float, b: float):
        pass

    def get_composition(self, phase, T, P):

        # TODO
        return self.composition

    def return_units(self, property_name, unit_system=None):

        if unit_system is None:

            return_value = constants.get_units(property_name, self.unit_system)

        else:

            return_value = constants.get_units(property_name, unit_system)

        if "Unknown" in return_value:

            return ""

        else:

            return return_value

    @property
    def unit_system(self):

        try:
            return self.__unit_system

        except:
            return None

    @unit_system.setter
    def unit_system(self, unit_system_input):

        old_unit_system = self.unit_system
        self.__unit_system = unit_system_input

        try:

            self.set_unit_system(unit_system_input)

        except:

            self.set_unit_system(DEFAULT_UNIT_SYSTEM)
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

        # Evaluate Critical and Triple Point
        self.TC = self.base_calculate("", "TC", 0, 0)
        self.PC = self.base_calculate("", "PC", 0, 0)
        self.T_trip = self.base_calculate("", "TTRP", 0, 0)
        self.P_trip = self.base_calculate("", "PTRP", 0, 0)

        self.set_reference_state(old_unit_system=old_unit_system)

    @abstractmethod
    def set_unit_system(self, unit_system_input):

        pass

    @property
    def unit_is_mass_based(self):

        return not ("mol" in self.return_units("s"))

    @property
    def T_0_in_K(self):

        T_unit = self.return_units("T")
        TO, info = convert_variable(self.T_0, "T",  T_unit, "K")
        return TO

    def __init_subclass__(cls, **kwargs):

        super().__init_subclass__(**kwargs)
        HANDLER_SUBCLASSES[cls.__name__] = cls


def find_handler(input_handler_dict):

    for handler_dict in ACTIVE_HANDLERS:

        if dicts_are_equal(handler_dict, input_handler_dict):
            return handler_dict["instance"]

    return None


def dicts_are_equal(curr_dict, other_dict):

    for key in ["fluids", "composition", "unit_system", "class"]:

        if not (curr_dict[key] == other_dict[key]):
            return False

    return True


def init_handler(chosen_subclass: type(BaseHandler), fluids: list, composition: list, unit_system=DEFAULT_UNIT_SYSTEM):

    handler_dict = {

        "class": chosen_subclass,
        "fluids": fluids,
        "composition": composition,
        "unit_system": unit_system

    }

    new_subclass = find_handler(handler_dict)

    if new_subclass is None:

        new_subclass = chosen_subclass(fluids=fluids, composition=composition, unit_system=unit_system)
        handler_dict.update({

            "instance": new_subclass

        })

        ACTIVE_HANDLERS.append(handler_dict)

    return new_subclass
