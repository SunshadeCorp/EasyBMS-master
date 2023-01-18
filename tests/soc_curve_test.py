import unittest

from soc_curve import SocCurve


class SocCurveTest(unittest.TestCase):

    def setUp(self):
        self.soc_curve = SocCurve()

    def test_middle_value_1(self):
        voltage = 3.869
        soc = self.soc_curve.voltage_to_soc(voltage)
        expected_soc = 0.75
        self.assertAlmostEqual(soc, expected_soc, delta=0.001)

    def test_middle_value_2(self):
        voltage = 3.628
        soc = self.soc_curve.voltage_to_soc(voltage)
        expected_soc = 0.35
        self.assertAlmostEqual(soc, expected_soc, delta=0.001)

    def test_matching_value(self):
        voltage = 3.825
        soc = self.soc_curve.voltage_to_soc(voltage)
        expected_soc = 0.7
        self.assertAlmostEqual(soc, expected_soc, delta=0.001)

    def test_upper_value(self):
        voltage = 4.2
        soc = self.soc_curve.voltage_to_soc(voltage)
        self.assertGreater(soc, 1.0)
        self.assertLess(soc, 1.2)

    def test_lower_value(self):
        voltage = 3.3
        soc = self.soc_curve.voltage_to_soc(voltage)
        self.assertGreater(soc, -0.2)
        self.assertLess(soc, 0.0)

    def test_upper_out_of_range(self):
        voltage = 6.0
        with self.assertRaises(AssertionError):
            self.soc_curve.voltage_to_soc(voltage)

    def test_lower_out_of_range(self):
        voltage = -1.0
        with self.assertRaises(AssertionError):
            self.soc_curve.voltage_to_soc(voltage)

    def test_soc_to_voltage_out_of_range(self):
        with self.assertRaises(AssertionError):
            SocCurve.soc_to_voltage(-1.0)
        with self.assertRaises(AssertionError):
            SocCurve.soc_to_voltage(-0.1)
        with self.assertRaises(AssertionError):
            SocCurve.soc_to_voltage(1.1)
        with self.assertRaises(AssertionError):
            SocCurve.soc_to_voltage(10.0)

    def test_soc_to_voltage(self):
        self.assertAlmostEqual(SocCurve.soc_to_voltage(0.75), 3.869, delta=0.01)
        self.assertAlmostEqual(SocCurve.soc_to_voltage(0.35), 3.628, delta=0.01)
        self.assertAlmostEqual(SocCurve.soc_to_voltage(0.7), 3.825, delta=0.01)

        
if __name__ == '__main__':
    unittest.main()
