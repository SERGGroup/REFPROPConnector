from REFPROPConnector.refprop_calculator import AbstractThermodynamicPoint
from itertools import cycle
from tqdm import tqdm
import numpy as np


class DiagramPlotterOptions:

    def __init__(

            self, n_sat_points=500, n_isolines_points=500,
            x_variable="rho", x_var_range=(1, 1000), x_var_log=True,
            y_variable="P", y_var_range=(4, 15), y_var_log=True,
            isoline_ranges=None, plot_saturation=True

    ):

        if isoline_ranges is None:

            isoline_ranges = ({

                "T": (5, 150, 25),
                "H": (200, 450, 25)

            })

        self.n_sat_points = n_sat_points
        self.n_isolines_points = n_isolines_points
        self.plot_saturation = plot_saturation

        self.x_ax = x_variable
        self.x_ax_rng = x_var_range
        self.x_ax_log = x_var_log

        self.y_ax = y_variable
        self.y_ax_rng = y_var_range
        self.y_ax_log = y_var_log

        self.shown_isolines = isoline_ranges.keys()
        self.isoline_ranges = isoline_ranges
        self.__check_isolines()

    def __check_isolines(self):

        isoline_ranges = dict()
        other_yax = self.other_yax_variable

        if other_yax in self.shown_isolines:
            isoline_ranges.update({other_yax: self.isoline_ranges[other_yax]})

        for isoline_name in self.shown_isolines:
            if (isoline_name not in ["T", "P"]) and (not isoline_name == self.x_ax):
                isoline_ranges.update({isoline_name: self.isoline_ranges[isoline_name]})

        self.isoline_ranges = isoline_ranges
        self.shown_isolines = isoline_ranges.keys()

    @property
    def initialized_sat_values(self):

        return {

            "x": get_np_array(0, 0, 2 * self.n_sat_points),
            "y": get_np_array(0, 0, 2 * self.n_sat_points)

        }

    @property
    def initialized_isolines_values(self):

        isolines_dict = dict()

        if self.other_yax_variable in self.shown_isolines:

            isolines_dict.update({self.other_yax_variable: dict()})

        for isoline_name in self.shown_isolines:

            if (isoline_name not in ["T", "P"]) and (not isoline_name == self.x_ax):

                isolines_dict.update({isoline_name: dict()})

        return isolines_dict

    @property
    def other_yax_variable(self):

        if self.y_ax == "P":

            return "T"

        else:

            return "P"

    def get_range(self, n_points, return_x_ax=True):

        if return_x_ax:

            return get_np_array(self.x_ax_rng[0], self.x_ax_rng[1], n_points, log_scale=self.x_ax_log)

        else:

            return get_np_array(self.y_ax_rng[0], self.y_ax_rng[1], n_points, log_scale=self.y_ax_log)

    @property
    def calculate_tp_isoline(self):

        return self.other_yax_variable in self.shown_isolines

    @property
    def std_isolines_name(self):

        name_list = list()

        for isoline_name in self.shown_isolines:

            if (isoline_name not in ["T", "P"]) and (not isoline_name == self.x_ax):

                name_list.append(isoline_name)

        return name_list


class DiagramPlotter:

    def __init__(self, point: AbstractThermodynamicPoint, options: DiagramPlotterOptions = None):

        self.support_point = point.duplicate()

        if options is not None:
            self.options = options

        else:
            self.options = DiagramPlotterOptions()

        self.sat_values = self.options.initialized_sat_values
        self.isolines_values = self.options.initialized_isolines_values

    def calculate(self):

        self.sat_values = self.options.initialized_sat_values
        self.isolines_values = self.options.initialized_isolines_values

        self.__calculate_saturation_condition()
        self.__calculate_iso_lines()

    def __calculate_saturation_condition(self):

        if self.options.plot_saturation:

            y_crit = self.__get_y_critical_point()

            if self.options.y_ax_rng[0] < y_crit < self.options.y_ax_rng[1]:

                y_values = get_np_array(

                    self.options.y_ax_rng[0], y_crit,
                    self.options.n_sat_points, log_scale=self.options.y_ax_log

                )

            elif y_crit > self.options.y_ax_rng[1]:

                y_values = get_np_array(

                    self.options.y_ax_rng[0], self.options.y_ax_rng[1],
                    self.options.n_sat_points, log_scale=self.options.y_ax_log

                )

            else:

                self.options.plot_saturation = False
                return

            self.sat_values = self.options.initialized_sat_values
            pbar_sat = tqdm(desc="Calculating Saturation Points", total=self.options.n_sat_points)

            for i in range(self.options.n_sat_points):

                self.sat_values["y"][i] = y_values[i]
                self.sat_values["y"][-1 - i] = y_values[i]

                self.support_point.set_variable(self.options.y_ax, y_values[i])
                self.support_point.set_variable("Q", 0)
                self.sat_values["x"][i] = self.support_point.get_variable(self.options.x_ax)

                self.support_point.set_variable(self.options.y_ax, y_values[i])
                self.support_point.set_variable("Q", 1)
                self.sat_values["x"][-1 - i] = self.support_point.get_variable(self.options.x_ax)

                pbar_sat.update(1)

            pbar_sat.close()

    def __calculate_iso_lines(self):

        if self.options.calculate_tp_isoline:

            self.__calculate_iso_tp_lines()

        for isoline_name in self.options.std_isolines_name:

            self.__calculate_iso_val_lines(isoline_name)

    def __calculate_iso_tp_lines(self):

        if self.options.calculate_tp_isoline:

            y_max = self.options.y_ax_rng[1] * 2
            tp_var = self.options.other_yax_variable
            x_var_arr = self.options.get_range(self.options.n_isolines_points, return_x_ax=True)
            tp_range_spec = self.options.isoline_ranges[tp_var]
            tp_range = get_np_array(range_min=tp_range_spec[0], range_max=tp_range_spec[1], n_elements=tp_range_spec[2])

            if tp_var == "T":

                tp_crit = self.support_point.RPHandler.TC

            else:

                tp_crit = self.support_point.RPHandler.PC

            pbar_iso_t = tqdm(desc="iso-T lines calculation", total=self.options.n_isolines_points * len(tp_range))

            for tp in tp_range:

                x_var_list = list()
                y_var_list = list()

                y_sat = 0.
                x_sat = [0., 0.]

                if tp < tp_crit:

                    self.support_point.set_variable(tp_var, tp)
                    self.support_point.set_variable("Q", 0)
                    x_sat[0] = self.support_point.get_variable(self.options.x_ax)

                    self.support_point.set_variable(tp_var, tp)
                    self.support_point.set_variable("Q", 1)
                    x_sat[1] = self.support_point.get_variable(self.options.x_ax)

                    y_sat = self.support_point.get_variable(self.options.y_ax)

                self.support_point.set_variable(self.options.y_ax, y_max)
                self.support_point.set_variable(tp_var, tp)

                # x_var_list.append(self.support_point.get_variable(self.options.x_ax))
                # y_var_list.append(y_max)

                for var in x_var_arr:

                    if x_sat[0] < var < x_sat[1]:

                        x_var_list.append(var)
                        y_var_list.append(y_sat)

                    else:

                        self.support_point.set_variable(self.options.x_ax, var)
                        y_res = self.support_point.get_variable(self.options.y_ax)

                        if 0 < y_res <= y_max:

                            x_var_list.append(var)
                            y_var_list.append(y_res)

                    pbar_iso_t.update(1)

                if len(x_var_list) > 0:

                    self.isolines_values[tp_var].update({

                        '{:.0f} {}'.format(tp, self.support_point.get_unit(tp_var)): {

                            "y": y_var_list,
                            "x": x_var_list,

                        }

                    })

            pbar_iso_t.close()

    def __calculate_iso_val_lines(self, val):

        x_var_arr = self.options.get_range(self.options.n_isolines_points, return_x_ax=True)
        val_range_spec = self.options.isoline_ranges[val]
        val_range = get_np_array(

            range_min=val_range_spec[0],
            range_max=val_range_spec[1],
            n_elements=val_range_spec[2]

        )

        pbar_iso_val = tqdm(

            desc="iso-{} lines calculation".format(val),
            total=self.options.n_isolines_points * len(val_range)

        )

        for curr_val in val_range:

            x_var_list = list()
            y_var_list = list()
            self.support_point.set_variable(val, curr_val)

            for curr_x_var in x_var_arr:

                self.support_point.set_variable(self.options.x_ax, curr_x_var)
                y_res = self.support_point.get_variable(self.options.y_ax)

                if y_res > 0:

                    x_var_list.append(curr_x_var)
                    y_var_list.append(y_res)

                pbar_iso_val.update(1)

            if len(x_var_list) > 0:

                self.isolines_values[val].update({

                    '{:.0f} {}'.format(curr_val, self.support_point.get_unit(val)): {

                        "y": y_var_list,
                        "x": x_var_list,

                    }

                })

        pbar_iso_val.close()

    def __get_y_critical_point(self):

        if self.options.y_ax == "P":

            return self.support_point.RPHandler.PC

        else:

            return self.support_point.RPHandler.TC

    def plot(self, ax_1):

        # plot_saturation
        if self.options.plot_saturation:
            ax_1.plot(self.sat_values["x"], self.sat_values["y"], linewidth=2, color="black")

        lines = ["--", "-.", ":"]
        line_cycler = cycle(lines)
        isolines = self.isolines_values

        for line_key in isolines.keys():

            width = 0.4
            color = "black"
            line_style = next(line_cycler)

            for key in isolines[line_key].keys():

                lines.append(ax_1.plot(

                    isolines[line_key][key]["x"], isolines[line_key][key]["y"],
                    linewidth=width, color=color, alpha=0.5,
                    linestyle=line_style, label=key

                )[0])

        if self.options.y_ax_log:
            ax_1.set_yscale("log")

        if self.options.x_ax_log:
            ax_1.set_xscale("log")

        ax_1.set_xlim(left=self.options.x_ax_rng[0], right=self.options.x_ax_rng[1])
        ax_1.set_ylim(bottom=self.options.y_ax_rng[0], top=self.options.y_ax_rng[1])

        ax_1.set_xlabel(

            r'${}\ [{}]$'.format(self.options.x_ax, self.support_point.get_unit(self.options.x_ax)),
            fontsize='large', loc='right',

        )

        ax_1.set_ylabel(

            r'${}\ [{}]$'.format(self.options.y_ax, self.support_point.get_unit(self.options.y_ax)),
            fontsize='large', loc='top',

        )

        return ax_1


def get_np_array(range_min, range_max, n_elements=10, log_scale=False):

    if log_scale:
        return np.power(range_max / range_min, np.array(range(n_elements)) / (n_elements - 1)) * range_min

    else:
        return np.array(range(n_elements)) / (n_elements - 1) * (range_max - range_min) + range_min
