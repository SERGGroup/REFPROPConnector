from .refprop_names_tree import RefPropUnitConverterTree as __RP_conv_tree
from .refprop_names_tree import RefPropDerivativesTree as __RP_der_tree
from .refprop_names_tree import RefPropNamesTree as __RP_name_tree
import os


CURRENT_DIR = os.path.dirname(__file__)
__REFPROP_NAME_TREE = __RP_name_tree.initialize_from_xml()
__REFPROP_CONV_TREE = __RP_conv_tree.initialize_from_xml()
__REFPROP_DER_TREE = __RP_der_tree.initialize_from_xml()

def get_refprop_name(name: str):

    return __REFPROP_NAME_TREE.get_refprop_name(name.lower())


def get_units(name: str, unit_system: str):

    unit_system = unit_system.upper()
    units_dict = __REFPROP_NAME_TREE.get_units_dict(name.lower())

    if units_dict is not None:

        if unit_system in units_dict.keys():

            return units_dict[unit_system]

        else:

            return "Unknown Unit System {}".format(unit_system)

    else:

        return "Unknown property name {}".format(name)


def get_all_refprop_names():
    return __REFPROP_NAME_TREE.append_refprop_names(list())


def get_all_unit_systems():
    units_dict = __REFPROP_NAME_TREE.get_units_dict("p")

    if units_dict is not None:
        return units_dict.keys()

    return None


def get_other_standard_names(refprop_name):
    return __REFPROP_NAME_TREE.append_other_standard_names(list(), refprop_name)


def get_derivative_info(num_name: str, den_name: str, fix_name: str):

    der_code = "D{}D{}_{}".format(

        get_refprop_name(num_name),
        get_refprop_name(den_name),
        get_refprop_name(fix_name)

    ).upper()

    return __REFPROP_DER_TREE.find_element(der_code)


def get_conversion_info(variable_name):
    return __REFPROP_CONV_TREE.get_conversion_information(variable_name.lower())

