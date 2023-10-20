from .Tools.units_converter import convert_variable, constants
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from .Support.resources.file_handler import RP_EXEC
from abc import ABC, abstractmethod
from sty import fg, bg, ef, rs
from copy import deepcopy
import warnings, sty


GLOBALCounter = 0
CODES_TO_BE_ITERATED = [

    "HQ", "SQ", "EQ",
    "QH", "QS", "QE"

]


class QualityIteration:

    def __init__(self, RPHandler, str_in: str, str_out: str, a: float, b: float):

        self.RPHandler = RPHandler
        self.str_in = str_in

        self.__identify_Q(a, b)
        self.__identify_T_range()
        self.__iterate_quality()

        self.result = self.RPHandler.calculate("TQ", str_out, self.T_limits[0], self.q_value)

    def __identify_Q(self, a, b):

        self.other_var = self.str_in.strip("Q")

        if self.str_in[0] == "Q":

            self.q_value = a
            self.var_value = b

        else:

            self.q_value = b
            self.var_value = a

    def __identify_T_range(self):

        min_T = self.RPHandler.calculate("EOSMIN", "T", 0., 0.)

        try:

            triple_T = self.RPHandler.calculate("TRIP", "T", 0., 0.)

        except:

            triple_T = -1000000

        self.min_T = max(min_T, triple_T)
        self.T_limits = [min_T, self.RPHandler.TC]

    def __iterate_quality(self):

        self.value_limits = [

            self.__calculate_var(self.T_limits[0]),
            self.__calculate_var(self.T_limits[1])

        ]

        if not (self.value_limits[0] * self.value_limits[1] < 0):
            raise Exception("Unable to perform {} flash".format(self.str_in))

        counter = 0
        while abs(self.T_limits[0] - self.T_limits[1]) > 10**-3 or counter > 30:
            counter += 1
            self.__quality_iteration_step()

    def __quality_iteration_step(self):

        # Bisection Calculation
        T_bis = (self.T_limits[1] + self.T_limits[0]) / 2
        bis_dict = self.__get_quality_iteration_step_result(T_bis)
        dict_list = [bis_dict]

        # Secant Calculation (if possible)
        T_val = self.T_limits
        res_val = self.value_limits
        T_sec = T_val[0] - res_val[0] / (res_val[1] - res_val[0]) * (T_val[1] - T_val[0])

        if self.min_T < T_sec < self.RPHandler.TC:

            sec_dict = self.__get_quality_iteration_step_result(T_sec)
            dict_list.append(sec_dict)

            # if possible check the interval between T_sec and T_bis
            if bis_dict["var_new"] * sec_dict["var_new"] < 0:
                dict_list.append({

                    "new_limits": {

                        "T": [bis_dict["T_new"], sec_dict["T_new"]],
                        "var": [bis_dict["var_new"], sec_dict["var_new"]]

                    },
                    "dT": abs(bis_dict["T_new"] - sec_dict["T_new"])

                })

        # take the minimum dt interval
        min_dict = bis_dict
        for res_dict in dict_list:

            if min_dict["dT"] > res_dict["dT"]:
                min_dict = res_dict

        self.T_limits = min_dict["new_limits"]["T"]
        self.value_limits = min_dict["new_limits"]["var"]

    def __get_quality_iteration_step_result(self, new_T):

        T_limits_new = deepcopy(self.T_limits)
        value_limits_new = deepcopy(self.value_limits)
        new_var = self.__calculate_var(new_T)

        if new_var * self.value_limits[1] < 0:

            T_limits_new[0] = new_T
            value_limits_new[0] = new_var

        else:

            T_limits_new[1] = new_T
            value_limits_new[1] = new_var

        return {

            "T_new": new_T,
            "var_new": new_var,
            "new_limits": {

                "T": T_limits_new,
                "var": value_limits_new

            },
            "dT": abs(T_limits_new[1] - T_limits_new[0])

        }

    def __calculate_var(self, T_value):

        value = self.RPHandler.calculate("TQ", self.other_var, T_value, self.q_value)
        error = value - self.var_value
        return error


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

        self.refprop = REFPROPFunctionLibrary(RP_EXEC)
        self.refprop.SETPATHdll(RP_EXEC)

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

        self.H_0 = self.calculate("TP", "H", self.T_0, self.P_0)
        self.S_0 = self.calculate("TP", "s", self.T_0, self.P_0)

    def calculate(self, str_in: str, str_out: str, a: float, b: float):

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
        self.refprop.SETFLUIDSdll('*'.join(self.fluids))
        return self.refprop.REFPROP1dll(str_in, str_out, self.SI, 1, a, b, self.composition).c

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

        # Evaluate Critical and Triple Point
        self.TC = self.calculate("", "TC", 0, 0)
        self.PC = self.calculate("", "PC", 0, 0)
        self.T_trip = self.calculate("", "TTRP", 0, 0)
        self.P_trip = self.calculate("", "PTRP", 0, 0)

        self.set_reference_state(old_unit_system=old_unit_system)

    @property
    def unit_is_mass_based(self):

        return not ("mol" in self.return_units("s"))

    @property
    def rp_version(self):

        return self.refprop.RPVersion()

    @property
    def T_0_in_K(self):

        T_unit = self.return_units("T")
        TO, info = convert_variable(self.T_0, "T",  T_unit, "K")
        return TO


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

    def convert(self, rp_handler:RefPropHandler, to_unit_system):

        value, info = convert_variable(

            self.value, self.refprop_name,
            rp_handler.return_units(self.refprop_name),
            rp_handler.return_units(self.refprop_name, to_unit_system)

        )

        # TODO implement conversion mass / mole based system

        return value

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
    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all",
                        unit_system="SI WITH C"):

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
        self.__reset_state_var_order()

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

    def __update_variables(self):

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

        if self.calculation_ready:

            not_none_variables = self.not_none_variables
            input_str = not_none_variables[0].refprop_name + not_none_variables[1].refprop_name

            if input_str not in CODES_TO_BE_ITERATED:

                value = self.RPHandler.calculate(

                    input_str,
                    REFPROP_CODE,
                    not_none_variables[0].value,
                    not_none_variables[1].value

                )

            else:

                P_value = self.RPHandler.calculate(

                    input_str,
                    "P",
                    not_none_variables[0].value,
                    not_none_variables[1].value

                )

                self.set_variable("P", P_value)
                value = self.__calculate_direct(REFPROP_CODE)

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
        self.__reset_state_var_order()

        if self.calculation_ready:

            self.__update_variables()

    def get_variable(self, variable_name: str):

        variable = self.__get_variable_from_name(variable_name)

        if variable is not None:

            if variable not in self.calculated_variables:

                self.__calculate_variable(variable)

            return variable.value

        if variable_name == "exergy":

            dh = self.get_variable("h") - self.RPHandler.H_0
            ds = self.get_variable("s") - self.RPHandler.S_0

            return dh - self.RPHandler.T_0_in_K * ds

        try:

            return self.__dict__[variable_name]

        except:

            return None

    def get_derivative(self, num_name: str, den_name: str, fix_name: str):

        if self.calculation_ready:

            info = constants.get_derivative_info(num_name, den_name, fix_name)

            if info is not None:

                rp_codes = info.refprop_codes

                if info.is_fraction:

                    a = self.__calculate_direct(rp_codes[0])
                    b = self.__calculate_direct(rp_codes[1])

                    return - a / b

                elif info.is_inverse:

                    return 1 / self.__calculate_direct(rp_codes[0])

                else:

                    return self.__calculate_direct(rp_codes[0])

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

    def __reset_state_var_order(self):

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
    def state_variables_refprop_names(self) -> list:

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

    @property
    def reference_state(self):

        reference = self.duplicate()
        reference.set_variable("T", self.RPHandler.T_0)
        reference.set_variable("P", self.RPHandler.P_0)

        return reference

    @reference_state.setter
    def reference_state(self, state):

        self.RPHandler.set_reference_state(

            T_0 = state.get_variable("T"),
            P_0 = state.get_variable("P"),
            T_0unit = state.get_unit("T"),
            P_0unit = state.get_unit("P")

        )

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

                target_point.set_variable(variable.refprop_name, variable.convert(

                    self.RPHandler, target_point.RPHandler.unit_system

                ))

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

                    variable_back.format(constants.get_units(variable.refprop_name, unit_system)) for variable in
                    variable_list

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

    def __init__(self, fluids: list, composition: list, rp_handler=None, other_variables="all", calculate_on_need="all",
                 unit_system="SI WITH C"):

        if rp_handler is None:

            rp_handler = RefPropHandler(fluids, composition, unit_system)

        super().__init__(rp_handler, other_variables=other_variables, calculate_on_need=calculate_on_need)

    def other_calculation(self):
        pass

    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all",
                        unit_system="SI WITH C"):

        return ThermodynamicPoint(fluids, composition, other_variables, calculate_on_need, unit_system)

    def duplicate(self):

        tp = ThermodynamicPoint(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            rp_handler=self.RPHandler,
            unit_system=self.RPHandler.unit_system,
            other_variables=self.inputs["other_variables"],
            calculate_on_need=self.inputs["calculate_on_need"]

        )

        self.copy_state_to(tp)
        return tp

    def get_alternative_unit_system(self, new_unit_system):

        rp_handler = RefPropHandler(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            new_unit_system

        )

        tp = ThermodynamicPoint(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            rp_handler=rp_handler,
            unit_system=new_unit_system,
            other_variables=self.inputs["other_variables"],
            calculate_on_need=self.inputs["calculate_on_need"]

        )

        self.copy_state_to(tp)
        return tp