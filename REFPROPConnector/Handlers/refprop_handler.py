import warnings

from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

from REFPROPConnector.Support.resources.file_handler import RP_EXEC
from .__base_handler import BaseHandler, DEFAULT_UNIT_SYSTEM, CODES_TO_BE_ITERATED, QualityIteration


class RefPropHandler(BaseHandler):

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

        self.refprop = REFPROPFunctionLibrary(RP_EXEC)
        self.refprop.SETPATHdll(RP_EXEC)

        super().__init__(fluids, composition, unit_system)

    def base_evaluate_dll(self, str_in: str, str_out: str, a: float, b: float):
        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

    def evaluate_dll(self, str_out: str, variable_a, variable_b, metastb=""):

        str_in = variable_a.refprop_name + variable_b.refprop_name + metastb
        a = variable_a.value
        b = variable_b.value

        if str_in in CODES_TO_BE_ITERATED:

            qi = QualityIteration(self, str_in, str_out, a, b)
            return qi.result

        if str_out == "Q":

            if self.unit_is_mass_based:

                str_out = "QMASS"

            else:

                str_out = "QMOLE"

        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

    def set_unit_system(self, unit_system_input):

        self.SI = self.refprop.GETENUMdll(0, unit_system_input).iEnum

    @property
    def rp_version(self):

        return self.refprop.RPVersion()
