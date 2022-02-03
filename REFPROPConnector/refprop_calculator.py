from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import REFPROPConnector.constants as constants
from abc import ABC, abstractmethod
from sty import fg, bg, ef, rs
import warnings, sty


GLOBALCounter = 0


class RefPropHandler:

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

        self.refprop = REFPROPFunctionLibrary(constants.RP_EXEC)
        self.refprop.SETPATHdll(constants.RP_EXEC)

        self.fluids = fluids
        self.composition = composition
        self.unit_system = unit_system

        self.TC = self.calculate("", "TC", 0, 0)
        self.PC = self.calculate("", "PC", 0, 0)

    def __initialize_reference_state(self):

        T_unit = self.return_units("T")
        P_unit = self.return_units("P")

        T_0 = 20        # °C
        P_0 = 101325    # Pa

        if T_unit == "C":

            # Celsius
            self.T_0 = T_0

        elif T_unit == "K":

            # Kelvin
            self.T_0 = T_0 + 273.15

        else:

            # Fahrenheit
            self.T_0 = T_0 * 9 / 5 + 32

        if P_unit == "Pa":

            # Pascal
            self.P_0 = P_0

        elif P_unit == "kPa":

            # kiloPascal
            self.P_0 = P_0 / 1000

        elif P_unit == "bar":

            # bar
            self.P_0 = P_0 / 100000

        elif P_unit == "MPa":

            # bar
            self.P_0 = P_0 / 100000

        else:

            # PSI
            self.P_0 = P_0 / 6894.7572931783

        self.H_0 = self.calculate("TP", "H", self.T_0, self.P_0)
        self.S_0 = self.calculate("TP", "s", self.T_0, self.P_0)

    def calculate(self, str_in: str, str_out: str, a: float, b: float):

        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

    def get_composition(self, phase, T, P):

        # TODO
        return self.composition

    def return_units(self, property_name):

        return_value = constants.get_units(property_name, self.unit_system)

        if "Unknown" in return_value:

            return ""

        else:

            return return_value

    @property
    def unit_system(self):

        return self.__unit_system

    @unit_system.setter
    def unit_system(self, unit_system_input):

        self.__unit_system = unit_system_input

        try:

            self.SI = self.refprop.GETENUMdll(0, self.__unit_system).iEnum

        except:

            self.SI = self.refprop.GETENUMdll(0, "SI WITH C").iEnum

            warning_message = (

                "{} unit system is not supported, "
                "{} has been used instead\n"
                "Check in the refprop manual for the correct"
                "name of the system that you wanted to use"

            ).format(self.__unit_system, "SI WITH C")

            warnings.warn(warning_message)
            self.__unit_system = "SI WITH C"

        self.__initialize_reference_state()


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


class AbstractThermodynamicPoint(ABC):

    @classmethod
    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all", unit_system="SI WITH C"):

        RP = RefPropHandler(fluids, composition, unit_system)
        return cls(RP, other_variables, calculate_on_need)

    def __init__(self, refprop: RefPropHandler, other_variables="all", calculate_on_need="all"):

        self.RPHandler = refprop
        self.inputs = {

            "other_variables": other_variables,
            "calculate_on_need": calculate_on_need

        }

        self.__initialize_state_variables()
        self.__initialize_other_variables(other_variables)
        self.reset_state_var_order()

        self.calculated_variables = list()
        self.__initialize_calculate_on_need_variables(calculate_on_need)

    def __initialize_state_variables(self):

        self.state_var_list = list()

        for variable_name in ["P", "T", "h", "s", "Q", "rho"]:

            new_variable = ThermodynamicVariable(variable_name)
            self.state_var_list.append(new_variable)

    def __initialize_other_variables(self, other_variables):

        self.other_variables = list()

        if other_variables is not None:

            if other_variables == "all":

                other_variables = constants.get_all_refprop_names()

            if type(other_variables) == list:

                state_variables_refprop_names = self.state_variables_refprop_names

                for variable_name in other_variables:

                    if not constants.get_refprop_name(variable_name) in state_variables_refprop_names:

                        new_variable = ThermodynamicVariable(variable_name)
                        self.other_variables.append(new_variable)

    def __initialize_calculate_on_need_variables(self, calculate_on_need):

        self.calculate_on_need_variables = list()

        if calculate_on_need is not None:

            if type(calculate_on_need) == list:

                for varible_name in calculate_on_need:

                    found_variable = self.__get_variable_from_name(varible_name)

                    if found_variable is not None:
                        self.calculate_on_need_variables.append(found_variable)

            elif calculate_on_need == "all":

                self.calculate_on_need_variables.extend(self.variables)

            elif calculate_on_need == "other":

                self.calculate_on_need_variables.extend(self.other_variables)

            elif calculate_on_need == "state":

                self.calculate_on_need_variables.extend(self.state_var_list)

    def __calculate(self):

        not_none_variables = self.not_none_variables
        self.calculated_variables = not_none_variables

        for variable in self.state_var_list:

            if variable in not_none_variables:

                variable.is_user_defined = True

            else:

                if variable not in self.calculate_on_need_variables:
                    self.__calculate_variable(variable)

        for variable in self.other_variables:

            if variable not in self.calculate_on_need_variables:
                self.__calculate_variable(variable)

        self.other_calculation()

    def __calculate_variable(self, variable):

        if self.calculation_ready:

            variable.value = self.__calculate_direct(variable.refprop_name)
            self.calculated_variables.append(variable)

    def __calculate_direct(self, REFPROP_CODE):

        global GLOBALCounter

        if self.calculation_ready:

            GLOBALCounter += 1

            not_none_variables = self.not_none_variables
            input_str = not_none_variables[0].refprop_name + not_none_variables[1].refprop_name

            value = self.RPHandler.calculate(

                input_str,
                REFPROP_CODE,
                not_none_variables[0].value,
                not_none_variables[1].value

            )

            return value

        return None

    @abstractmethod
    def other_calculation(self):
        pass

    def set_variable(self, variable_name: str, variable_value: float):

        input_refprop_name = constants.get_refprop_name(variable_name)

        for variable in self.state_var_list:

            if variable.refprop_name == input_refprop_name:

                variable.value = variable_value
                variable.order = 0

                break

        self.state_var_list.sort()
        self.reset_state_var_order()

        if self.calculation_ready:

            self.__calculate()

    def get_variable(self, variable_name: str):

        variable = self.__get_variable_from_name(variable_name)

        if variable is not None:

            if variable not in self.calculated_variables:

                self.__calculate_variable(variable)

            return variable.value

        if variable_name == "exergy":

            h = self.get_variable("h")
            s = self.get_variable("s")

            return (h - self.RPHandler.H_0) - self.RPHandler.T_0 * (s - self.RPHandler.S_0)

        try:

            return self.__dict__[variable_name]

        except:

            return None

    def get_composition(self, phase):

        if self.calculation_ready:

            Q = self.get_variable("Q")

            if 0 < Q < 1:

                T = self.get_variable("T")
                P = self.get_variable("P")
                self.RPHandler.get_composition(phase, T, P)

            else:

                return self.composition

    def get_unit(self, variable_name: str):

        return self.RPHandler.return_units(variable_name)

    def __get_variable_from_name(self, variable_name: str):

        input_refprop_name = constants.get_refprop_name(variable_name.lower())

        for variable in self.variables:

            if variable.refprop_name == input_refprop_name:
                return variable

        return None

    def reset_state_var_order(self):

        counter = 1
        for variable in self.state_var_list:
            variable.order = counter
            counter += 1

    @property
    def calculation_ready(self):

        counter = 0

        for variable in self.state_var_list:

            if not variable.is_empty:
                counter += 1

        if counter > 2:

            return True

        elif counter == 2:

            __Q = self.__get_variable_from_name("Q")

            if not __Q.is_empty:

                if (__Q.value <= 1) and (__Q.value >= 0):
                    return True

                else:
                    return False

            return True

        else:

            return False

    @property
    def not_none_variables(self) -> list:

        return_list = list()

        for variable in self.state_var_list:

            if not variable.is_empty:

                return_list.append(variable)

                if len(return_list) == 2:
                    break

        return return_list

    @property
    def state_variables_refprop_names(self)->list:

        return_list = list()
        for variable in self.state_var_list:

            return_list.append(variable.refprop_name)

        return return_list

    @property
    def variables(self):

        variables = list()
        variables.extend(self.state_var_list)
        variables.extend(self.other_variables)

        return variables

    @property
    def composition(self):

        return self.RPHandler.composition

    @composition.setter
    def composition(self, new_composition: list):

        self.RPHandler.composition = new_composition

    @staticmethod
    def print_global_counter(reset=True):

        global GLOBALCounter
        print(GLOBALCounter)

        if reset:
            GLOBALCounter = 0

    @abstractmethod
    def duplicate(self):
        """
            used to create a copy of the point for further calculations
            in programming it in subclasses use the input dictionary to recover original inputs

            don't forget to copy the current state defined by the user:

                self.copy_state_to(new_point)

        """
        pass

    def copy_state_to(self, target_point):

        for variable in self.state_var_list[:2]:

            if variable.is_empty:
                break

            else:
                target_point.set_variable(variable.refprop_name, variable.value)

        return target_point

    def list_properties(self):

        string_to_display = """
        
        -----------------------------------------------------------
        -----------------------------------------------------------
            
                        REFPROP_Connector VARIABLES
                
                (if you need more of them to be implemented
                please contact pietro.ungar@unifi.it)
        
        -----------------------------------------------------------
        -----------------------------------------------------------"""

        string_to_display += """
        
            STATE VARIABLES
            (variables that can be set in order to define the 
            thermodynamic state)
            """

        string_to_display += self.__return_variable_list_str(self.state_var_list)

        string_to_display += """
        -----------------------------------------------------------
        
            OTHER VARIABLES
            """

        string_to_display += self.__return_variable_list_str(self.other_variables)

        print(string_to_display)

    def list_unit_systems(self, simplified_display=False, step=4):

        i = 0

        if simplified_display:

            sty.mute(fg, bg, ef, rs)

        else:

            sty.unmute(fg, bg, ef, rs)

        string_to_display = """

                -----------------------------------------------------------
                -----------------------------------------------------------

                              REFPROP_Connector UNIT SYSTEMS

                        (if you need more of them to be implemented
                        please contact pietro.ungar@unifi.it)"""

        while i < len(self.variables):

            string_to_display += """

                -----------------------------------------------------------
                -----------------------------------------------------------

            """

            if  i + step < len(self.variables):

                string_to_display += self.__return_variable_unit_str(self.variables[i: i + step])

            else:

                string_to_display += self.__return_variable_unit_str(self.variables[i:])

            i = i + step

        print(string_to_display)

    def __return_variable_list_str(self, variable_list):

        string_to_display = """
            {:<15} {:<25} {:<10}
            """.format("REFPROP NAME:", "ALTERNATIVE NAMES:", "UNIT:")

        for variable in variable_list:

            refprop_name = variable.refprop_name
            other_std_names = constants.get_other_standard_names(refprop_name)
            unit = self.get_unit(refprop_name)

            string_to_display += """
            {:<15} {:<25}  {:<10}
            """.format(refprop_name.upper(), other_std_names[0], unit)

            string_to_display += """
            """.join("{:<15} {:<25}".format("", std_name) for std_name in other_std_names[1:])
            string_to_display += "\n"

        return string_to_display

    def __return_variable_unit_str(self, variable_list):

        name_format = " {:15s}"
        variable_format = " {:20s}"

        name_bold = ef.bold + name_format + ef.rs
        name_back = bg.li_yellow + name_format + bg.rs
        variable_bold = ef.bold + variable_format + ef.rs
        variable_back = bg.li_yellow + variable_format + bg.rs

        string_to_display = "\n" + name_format.format("") + " ".join(

            variable_bold.format(variable.refprop_name.upper()) for variable in variable_list

        ) + "\n\n"

        for unit_system in constants.get_all_unit_systems():

            if unit_system == self.RPHandler.unit_system:

                string_to_display += name_back.format(unit_system)
                string_to_display += "".join(

                    variable_back.format(constants.get_units(variable.refprop_name, unit_system)) for variable in variable_list

                )

            else:

                string_to_display += name_bold.format(unit_system)
                string_to_display += "".join(

                    variable_format.format(constants.get_units(variable.refprop_name, unit_system)) for variable in
                    variable_list

                )

            string_to_display += "\n"

        return string_to_display


class ThermodynamicPoint(AbstractThermodynamicPoint):

    def __init__(self, fluids: list, composition: list, other_variables="all", calculate_on_need="all", unit_system="SI WITH C"):

        RP = RefPropHandler(fluids, composition, unit_system)
        super().__init__(RP, other_variables=other_variables, calculate_on_need=calculate_on_need)

    def other_calculation(self):
        pass

    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all", unit_system="SI WITH C"):

        return ThermodynamicPoint(fluids, composition, other_variables, calculate_on_need, unit_system)

    def duplicate(self):

        tp = ThermodynamicPoint(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            unit_system=self.RPHandler.unit_system,
            other_variables=self.inputs["other_variables"],
            calculate_on_need=self.inputs["calculate_on_need"]

        )

        self.copy_state_to(tp)
        return tp