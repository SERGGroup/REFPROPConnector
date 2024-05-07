from copy import deepcopy

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

        self.result = self.RPHandler.base_calculate("TQ", str_out, self.T_limits[0], self.q_value)

    def __identify_Q(self, a, b):

        self.other_var = self.str_in.strip("Q")

        if self.str_in[0] == "Q":

            self.q_value = a
            self.var_value = b

        else:

            self.q_value = b
            self.var_value = a

    def __identify_T_range(self):

        min_T = self.RPHandler.base_calculate("EOSMIN", "T", 0., 0.)

        try:

            triple_T = self.RPHandler.base_calculate("TRIP", "T", 0., 0.)

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

        value = self.RPHandler.base_calculate("TQ", self.other_var, T_value, self.q_value)
        error = value - self.var_value
        return error