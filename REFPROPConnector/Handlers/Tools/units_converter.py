import REFPROPConnector.Support.constants as constants


def convert_variable(variable_value, variable_name, from_unit, to_unit):

    conversion_info = constants.get_conversion_info(variable_name)

    if conversion_info.conversion_function == "multiply":

        result = __conversion_multiply(variable_value, conversion_info, from_unit, to_unit)

    elif conversion_info.conversion_function == "sum_mult":

        result = __conversion_sum_mult(variable_value, conversion_info, from_unit, to_unit)

    elif from_unit == to_unit:

        result = variable_value

    else:

        return None, conversion_info

    return result, conversion_info


def __conversion_multiply(value, conversion_info, from_unit, to_unit):

    multiplier = conversion_info.conversion_dict[from_unit]["mult"]
    tmp_value = value * multiplier

    multiplier = conversion_info.conversion_dict[to_unit]["mult"]
    return tmp_value / multiplier


def __conversion_sum_mult(value, conversion_info, from_unit, to_unit):

    mult = conversion_info.conversion_dict[from_unit]["mult"]
    sum = conversion_info.conversion_dict[from_unit]["sum"]
    tmp_value = (value + sum) * mult

    mult = conversion_info.conversion_dict[to_unit]["mult"]
    sum = conversion_info.conversion_dict[to_unit]["sum"]
    return tmp_value / mult - sum
