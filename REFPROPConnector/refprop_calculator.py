import warnings

from scipy.integrate import solve_ivp
from abc import ABC, abstractmethod
from sty import fg, bg, ef, rs
import sty


from REFPROPConnector.Handlers import (

    RefPropHandler, CODES_TO_BE_ITERATED, init_handler,
    ThermodynamicVariable, constants, DEFAULT_UNIT_SYSTEM

)


class AbstractThermodynamicPoint(ABC):

    @classmethod
    def init_from_fluid(

            cls, fluids: list, composition: list,
            other_variables="all", calculate_on_need="all",
            unit_system=DEFAULT_UNIT_SYSTEM

    ):

        RP = init_handler(

            chosen_subclass=RefPropHandler,
            fluids=fluids, composition=composition,
            unit_system=unit_system

        )
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
        self.__metastability = ""
        self.__tmp_si_point = None

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

                    REFPROP_CODE,
                    not_none_variables[0],
                    not_none_variables[1],
                    metastb=self.__metastability

                )

            else:

                P_value = self.RPHandler.calculate(

                    "P",
                    not_none_variables[0],
                    not_none_variables[1],
                    metastb=self.__metastability

                )

                self.set_variable("P", P_value)
                value = self.__calculate_direct(REFPROP_CODE)

            return value

        return None

    @abstractmethod
    def other_calculation(self):
        pass

    def set_variable(self, variable_name: str, variable_value: float, other_unit_system=None):

        input_refprop_name = constants.get_refprop_name(variable_name)

        for variable in self.state_var_list:

            if variable.refprop_name == input_refprop_name:

                if other_unit_system is None:

                    variable.value = variable_value

                else:

                    variable.set_from_different_us(variable_value, self.RPHandler, other_unit_system)

                variable.order = 0

                break

        self.state_var_list.sort()
        self.__reset_state_var_order()

        if self.calculation_ready:

            self.__update_variables()

    def get_variable(self, variable_name: str, other_unit_system=None):

        variable = self.__get_variable_from_name(variable_name)

        if variable is not None:

            if variable not in self.calculated_variables:

                self.__calculate_variable(variable)

            if other_unit_system is None:

                return variable.value

            else:

                return variable.convert(

                    rp_handler=self.RPHandler,
                    to_unit_system=other_unit_system

                )

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

    def get_second_derivative(self, num_name: str, den_name: str, other_den_name=None):

        if self.calculation_ready:

            if other_den_name is not None:

                info = constants.get_second_derivative_info(num_name, den_name, other_den_name)

            else:

                info = constants.get_second_derivative_info(num_name, den_name)

            if info is not None:

                rp_codes = info.refprop_codes
                return self.__calculate_direct(rp_codes[0])

        return None

    def evaluate_RP_code(self, rp_code):

        return self.__calculate_direct(rp_code)

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

    @abstractmethod
    def get_alternative_unit_system(self, new_unit_system):

        rp_handler = init_handler(

            chosen_subclass=RefPropHandler,
            fluids=self.RPHandler.fluids,
            composition=self.RPHandler.composition,
            unit_system=new_unit_system

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

    @property
    def metastability(self):


        if self.__metastability == "L":

            return "Liquid"

        if self.__metastability == "V":

            return "Vapour"

        return "Equilibrium"

    @metastability.setter
    def metastability(self, metastability: str):

        metastability = metastability.lower()
        if metastability == "liq" or metastability == "liquid" or metastability == "v" or metastability == ">":

            self.__metastability = "L"

        elif metastability == "vap" or metastability == "vapour" or metastability == "vapor" or metastability == "v" or metastability == "<":

            self.__metastability = "V"

        else:

            self.__metastability = ""

    def get_static_point(self, speed, keep_metastability=False, integrate=True):

        return self.__get_dynamic_variation(

            mult=-1, speed=speed,
            keep_metastability=keep_metastability,
            integrate=integrate

        )

    def get_stagnation_point(self, speed, keep_metastability=False, integrate=True):

        return self.__get_dynamic_variation(

            mult=1, speed=speed,
            keep_metastability=keep_metastability,
            integrate=integrate

        )

    def __get_dynamic_variation(self, mult, speed, keep_metastability=False, integrate=True):

        other_point = self.duplicate()
        si_unit_system = "MASS BASE SI"

        if self.__tmp_si_point is None:
            self.__tmp_si_point = self.get_alternative_unit_system(si_unit_system)

        self.copy_state_to(self.__tmp_si_point)

        if keep_metastability:
            other_point.metastability = self.__metastability

        h0 = self.get_variable("H", other_unit_system=si_unit_system)
        p0 = self.get_variable("P", other_unit_system=si_unit_system)
        s0 = self.get_variable("S", other_unit_system=si_unit_system)
        dh_dyn = speed ** 2 / 2

        if not integrate:

            dp_dyn = dh_dyn * self.__tmp_si_point.get_variable("rho")

        else:

            try:

                self.__tmp_si_point.set_variable("H", h0 + mult * dh_dyn)
                self.__tmp_si_point.set_variable("S", s0)
                dp_dyn = mult * (self.__tmp_si_point.get_variable("P") - p0)

            except:

                def f(t, y):

                    self.__tmp_si_point.set_variable("H", h0 + mult * t)
                    self.__tmp_si_point.set_variable("P", p0 + mult * y[0])

                    return self.__tmp_si_point.get_variable("rho")

                try:

                    sol = solve_ivp(f, [0, dh_dyn], [0], t_eval=[dh_dyn])
                    dp_dyn = sol.y[0][0]

                except:

                    warnings.warn("It was impossible to reach integral dynamic solution, constant rho solution returned instead")
                    dp_dyn = dh_dyn * self.__tmp_si_point("rho")

        other_point.set_variable("H", h0 + mult * dh_dyn, other_unit_system=si_unit_system)
        other_point.set_variable("P", p0 + mult * dp_dyn, other_unit_system=si_unit_system)

        return other_point

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

            if i + step < len(self.variables):

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

    def __eq__(self, other):

        """check if this is equal to another instance"""
        if not (self.calculation_ready and other.calculation_ready):
            return False

        if not (self.RPHandler.fluids == other.RPHandler.fluids):
            return False

        if not (self.RPHandler.composition == other.RPHandler.composition):
            return False

        if not (self.get_variable("P") == other.get_variable("P", other_unit_system=self.RPHandler.unit_system)):
            return False

        if not (self.get_variable("rho") == other.get_variable("rho", other_unit_system=self.RPHandler.unit_system)):
            return False

        return True


class ThermodynamicPoint(AbstractThermodynamicPoint):

    def __init__(self, fluids: list, composition: list, rp_handler=None, other_variables="all", calculate_on_need="all",
                 unit_system="SI WITH C"):

        if rp_handler is None:

            rp_handler = init_handler(

                chosen_subclass=RefPropHandler,
                fluids=fluids, composition=composition,
                unit_system=unit_system

            )

        super().__init__(rp_handler, other_variables=other_variables, calculate_on_need=calculate_on_need)

    def other_calculation(self):
        pass

    @classmethod
    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all", unit_system="SI WITH C"):

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

        rp_handler = init_handler(

            chosen_subclass=RefPropHandler,
            fluids=self.RPHandler.fluids,
            composition=self.RPHandler.composition,
            unit_system=new_unit_system

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
    