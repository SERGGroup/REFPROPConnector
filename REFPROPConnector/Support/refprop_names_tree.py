from REFPROPConnector.Support.resources.file_handler import get_refprop_name_xml
from abc import ABC, abstractmethod


class __AbstractTree(ABC):
    """

        Abstract class for a Binary tree object.

        Each node is defined by a search payload and an optional payload

        Search payload will be compared during binary research hence it has to be UNIQUE and to support comparison
        operation (i.e. "<"; ">"; "==")

        Payload can be every kind of object, if needed an initialization can be performed overwriting the init_payload
        function


    """

    def __init__(self):

        self.search_value = None
        self.left_tree = None
        self.right_tree = None

    def append_value(self, search_value, payload):

        if self.is_empty:

            self.search_value = search_value
            self.init_payload(payload)

            self.left_tree = self.init_empty_self()
            self.right_tree = self.init_empty_self()

        else:

            if self.search_value < search_value:

                self.right_tree.append_value(search_value, payload)

            elif self.search_value > search_value:

                self.left_tree.append_value(search_value, payload)

    def find_element(self, search_value):

        if self.is_empty:

            return None

        else:

            if self.search_value == search_value:

                return self

            elif self.search_value < search_value:

                return self.right_tree.find_element(search_value)

            else:

                return self.left_tree.find_element(search_value)

    @property
    def is_empty(self):

        return self.search_value is None

    @abstractmethod
    def init_payload(self, payload):

        """

            Abstract method for the initialization of the payload. It is called by the append_value function during the
            initialization of a new node (hence when the program finds the right empty spot to add the new node)

            It is useful to add new attributes to the tree node if needed

        """

    @classmethod
    @abstractmethod
    def init_empty_self(self):

        """

            This method is called by the append_value function during the initialization of the new left and right
            branches of the tree. It has to be overwritten in sub-classes even if the best approach for this overwriting
            is simply to call the __init__ method of the subclass as in the example below:

                @classmethod
                def init_empty_self(cls):

                    return cls()

            more complex initialization can be performed if needed.

            IMPORTANT NOTES:

                - keep self.search_value = None otherwise the software will not identify the initialized node as empty!
                - any modification to self.left_tree and self.right_tree will not be effective as the both will be
                  overwritten by append_value when called.

        """

        pass


class RefPropNamesTree(__AbstractTree):

    def __init__(self):

        super().__init__()
        self.refprop_name = None
        self.units_dict = None

    def init_payload(self, payload):

        self.refprop_name = payload["RP_Name"]
        self.units_dict = payload["units_dict"]

    @classmethod
    def init_empty_self(cls):

        return cls()

    @classmethod
    def initialize_from_xml(cls):

        refprop_names_tree = cls()
        root = get_refprop_name_xml()

        for element in root.findall("refprop_name"):

            ref_prop_name = element.attrib["name"].upper()

            unit_dict = dict()

            for unit in element.find("units").findall("unit"):

                unit_dict.update({unit.attrib["name"]: unit.attrib["unit"]})

            value_dict = {"RP_Name": ref_prop_name, "units_dict": unit_dict}

            refprop_names_tree.append_value(ref_prop_name.lower(), value_dict)

            for std_name in element.find("std_names").findall("std_name"):

                refprop_names_tree.append_value(std_name.attrib["name"].lower(), value_dict)

        return refprop_names_tree

    def get_refprop_name(self, input_std_name):

        element_found = self.find_element(input_std_name)

        if element_found is not None:
            return element_found.refprop_name

        return None

    def get_units_dict(self, input_std_name):

        element_found = self.find_element(input_std_name)

        if element_found is not None:
            return element_found.units_dict

        return None

    def append_refprop_names(self, initial_list: list) -> list:

        if self.is_empty:

            return initial_list

        else:

            new_list = self.right_tree.append_refprop_names(initial_list)
            new_list = self.left_tree.append_refprop_names(new_list)

            if self.refprop_name not in initial_list:
                new_list.append(self.refprop_name)

            return new_list

    def append_other_standard_names(self, initial_list: list, refprop_name) -> list:

        if self.is_empty:

            return initial_list

        else:

            new_list = self.right_tree.append_other_standard_names(initial_list, refprop_name)
            new_list = self.left_tree.append_other_standard_names(new_list, refprop_name)

            if self.refprop_name == refprop_name:

                if self.search_value not in initial_list and not self.search_value == refprop_name:
                    new_list.append(self.search_value)

            return new_list


class RefPropDerivativesTree(__AbstractTree):

    def __init__(self):

        super().__init__()

        self.refprop_codes = None
        self.is_inverse = False
        self.is_fraction = False

    def init_payload(self, payload):

        self.refprop_codes = payload["REFPROP_CODE"]

        self.is_inverse = (payload["INVERSE"] == str(True))
        self.is_fraction = (payload["FRACTION"] == str(True))

    @classmethod
    def init_empty_self(cls):

        return cls()

    @classmethod
    def initialize_from_xml(cls):

        derivatives_tree = cls()
        derivatives_list = cls.__init_derivatives_list()

        for der_dict in derivatives_list:

            derivatives_tree.append_value(der_dict["SEARCH_CODE"].upper(), der_dict)

        return derivatives_tree

    @classmethod
    def __init_derivatives_list(cls):

        """

            REFPROP provides the values of the partial derivatives of some variables

            - For the 'main_derivatives' properties (currently P, T, and D) it allows every combination of respective
                derivatives (i.e. dp/dT fixed D, dT/dP fixed D and so on).
                The syntax if the REFPROP call in this case is:

                    D{1}D{2}

                    where

                        {1} is the name of the numerator
                        {2} is the name of the denominator


            - For the 'other_derivatives' properties it allows only the calculation of the derivative of such property
                with respect to one 'main_derivatives' property. The syntax is:

                    D{1}D{2}_{3}

                    where

                        {1} is the name of the numerator
                        {2} is the name of the denominator
                        {3} is another main 'main_derivatives' property that is kept fixed

        """

        root = get_refprop_name_xml(get_derivatives_xml=True)

        main_der = root.find("main_derivatives_prop")
        other_der = root.find("other_derivatives_prop")

        main_der_list = list()
        other_der_list = list()
        derivatives_list = list()

        for element in main_der.findall("refprop_name"):
            main_der_list.append(element.attrib["name"].upper())

        for element in other_der.findall("refprop_name"):
            other_der_list.append(element.attrib["name"].upper())

        derivatives_list.extend(cls.__init_main_der_list(main_der_list, other_der_list))
        derivatives_list.extend(cls.__init_other_der_list(main_der_list, other_der_list))

        return derivatives_list

    @classmethod
    def __init_main_der_list(cls, main_der_list, other_der_list):

        derivatives_list = list()

        for num_name in main_der_list:

            for den_name in main_der_list:

                if not (num_name == den_name):

                    for fix_name in main_der_list:

                        if not (num_name == fix_name) and not (den_name == fix_name):

                            derivatives_list.append(cls.__get_derivatives_dict(num_name, den_name, fix_name, is_main=True))

                    for fix_name in other_der_list:

                        derivatives_list.append(cls.__get_derivatives_dict(num_name, den_name, fix_name, is_fraction=True))

        return derivatives_list

    @classmethod
    def __init_other_der_list(cls, main_der_list, other_der_list):

        derivatives_list = list()

        for num_name in other_der_list:

            for den_name in main_der_list:

                for fix_name in main_der_list:

                    if not (den_name == fix_name):

                        derivatives_list.append(cls.__get_derivatives_dict(num_name, den_name, fix_name))
                        derivatives_list.append(cls.__get_derivatives_dict(den_name, num_name, fix_name, is_inverse=True))

        return derivatives_list

    @staticmethod
    def __get_derivatives_dict(num_name, den_name, fix_name, is_main=False, is_inverse=False, is_fraction=False):

        search_code = "D{}D{}_{}".format(num_name, den_name, fix_name)

        if is_main:

            rp_code = ["D{}D{}".format(num_name, den_name)]

        elif is_inverse:

            rp_code = ["D{}D{}_{}".format(den_name, num_name, fix_name)]

        elif is_fraction:

            rp_code = [

                "D{}D{}_{}".format(fix_name, den_name, num_name),
                "D{}D{}_{}".format(fix_name, num_name, den_name)

            ]

        else:

            rp_code = [search_code]

        return {

            "SEARCH_CODE": search_code,
            "REFPROP_CODE": rp_code,

            "INVERSE": str(is_inverse),
            "FRACTION": str(is_fraction)

        }