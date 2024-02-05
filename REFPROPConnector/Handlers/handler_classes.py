import warnings

from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

from REFPROPConnector.Support.resources.file_handler import RP_EXEC
from .__base_handler import BaseHandler, DEFAULT_UNIT_SYSTEM


class RefPropHandler(BaseHandler):

    def __init__(self, fluids: list, composition: list, unit_system="SI WITH C"):

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

        super().__init__(fluids, composition, unit_system)
        self.refprop = REFPROPFunctionLibrary(RP_EXEC)
        self.refprop.SETPATHdll(RP_EXEC)

    def evaluate_dll(self, str_in: str, str_out: str, a: float, b: float):
        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

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

    @property
    def rp_version(self):

        return self.refprop.RPVersion()


class CoolpropHandler(BaseHandler):

    def __init__(self, fluids: list, composition: list, unit_system="SI WITH C"):

        super().__init__(fluids, composition, unit_system)
        self.refprop = REFPROPFunctionLibrary(RP_EXEC)
        self.refprop.SETPATHdll(RP_EXEC)
    
    def evaluate_dll(self, str_in: str, str_out: str, a: float, b: float):
        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

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
