from REFPROPConnector.Support.constants import get_refprop_name
from REFPROPConnector import ThermodynamicPoint
import unittest


class TestREFPROPConnector(unittest.TestCase):

    def test_init(self):

        ThermodynamicPoint(["air"], [1])
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


if __name__ == '__main__':
    unittest.main()
