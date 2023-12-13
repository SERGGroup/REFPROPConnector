from REFPROPConnector import ThermodynamicPoint, DiagramPlotter, DiagramPlotterOptions
from REFPROPConnector.Tools.units_converter import convert_variable
from REFPROPConnector.Support.constants import get_refprop_name
from matplotlib import pyplot as plt
import unittest


class TestREFPROPConnector(unittest.TestCase):

    def test_init(self):

        ThermodynamicPoint(["Carbon Dioxide"], [1])
        self.assertEqual(True, True)

    def test_list_properties(self):

        tp = ThermodynamicPoint(["air"], [1])
        tp.list_properties()
        self.assertEqual(True, True)

    def test_list_units(self):

        tp = ThermodynamicPoint(["air"], [1], unit_system="MASS BASE SI")
        tp.list_unit_systems()
        self.assertEqual(True, True)

    def test_search(self):

        rp_name = get_refprop_name("pressure")
        self.assertEqual("P", rp_name)

    def test_convert(self):

        rp_name, info = convert_variable(32, "T", "F", "K")
        self.assertEqual(273.15, rp_name)

        rp_name, info = convert_variable(1, "P", "MPa", "Pa")
        self.assertEqual(1e6, rp_name)

        rp_name, info = convert_variable(1, "H", "J/g", "J/kg")
        self.assertEqual(1e3, rp_name)

    def test_convert_unit_system(self):

        tp = ThermodynamicPoint(["Carbon Dioxide"], [1])
        tp.set_variable("T", 20)
        tp.set_variable("P", 1)

        tp_new = tp.get_alternative_unit_system("MASS BASE SI")

        self.assertEqual(20+273.15, tp_new.get_variable("T"))

    def test_copy(self):

        tp = ThermodynamicPoint(["air"], [1])

        tp.set_variable("T", 20)
        tp.set_variable("P", 0.1)

        new_tp = tp.duplicate()
        check_equal = tp.get_variable("h") == new_tp.get_variable("h")

        tp.set_variable("T", 30)
        check_different = not(tp.get_variable("h") == new_tp.get_variable("h"))

        self.assertEqual(True, check_equal and check_different)

    def test_derivative(self):

        tp = ThermodynamicPoint(["carbon dioxide"], [1])

        tp.set_variable("T", 90)
        tp.set_variable("P", 15)

        print(tp.get_derivative("T", "P", "H"))

        self.assertEqual(True, True)

    def test_second_derivative(self):

        tp = ThermodynamicPoint(["carbon dioxide"], [1])

        tp.set_variable("T", 90)
        tp.set_variable("P", 15)

        print(tp.get_second_derivative("T", "P"))

        self.assertEqual(True, True)

    def test_evaluate_direct(self):

        tp = ThermodynamicPoint(["carbon dioxide"], [1])

        tp.set_variable("T", 90)
        tp.set_variable("P", 15)

        a = tp.evaluate_RP_code("D2PDTD")
        b = tp.get_second_derivative("P", "T", "rho")
        print(a)
        print(b)

        self.assertEqual(a, b)

    def test_reference_state(self):

        tp = ThermodynamicPoint(["carbon dioxide"], [1])

        T_ref = 10
        tp_ref = tp.duplicate()
        tp_ref.set_variable("T", T_ref)
        tp_ref.set_variable("P", 0.101325)

        tp.reference_state = tp_ref

        self.assertEqual(tp.reference_state.get_variable("T"), T_ref + 273.15)

    def test_QH_flash(self):

        tp = ThermodynamicPoint(["water"], [1])

        tp.set_variable("T", 150)
        tp.set_variable("Q", 0)
        h_new = tp.get_variable("h")

        new_state = tp.duplicate()
        new_state.set_variable("Q", 0.05)
        new_state.set_variable("h", h_new)

        print("{} - {}".format(

            tp.get_variable("P"),
            new_state.get_variable("P")

        ))

    def test_PH_flash(self):

        tp = ThermodynamicPoint(["water"], [1])

        tp.set_variable("T", 150)
        tp.set_variable("Q", 0.5)
        h_new = tp.get_variable("h")
        s_new = tp.get_variable("s")

        new_state = tp.duplicate()
        new_state.set_variable("s", s_new)
        new_state.set_variable("h", h_new)

        print("{} - {}".format(

            tp.get_variable("q"),
            new_state.get_variable("q")

        ))

    def test_diagram_plotter(self):

        tp = ThermodynamicPoint(["Carbon Dioxide"], [1])
        options = DiagramPlotterOptions(

            x_variable="T",
            x_var_range = (0, 150), x_var_log=False,
            y_var_range = (4, 15),
            isoline_ranges={

                "rho": (50, 1000, 25),
                "H": (200, 550, 25)

            }

        )
        plotter = DiagramPlotter(tp, options=options)
        plotter.calculate()

        fig, (ax_1) = plt.subplots(1, 1, dpi=200)
        fig.set_size_inches(10, 5)
        plotter.plot(ax_1)
        plt.show()


if __name__ == '__main__':
    unittest.main()
