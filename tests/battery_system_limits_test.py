import unittest

from battery_system import BatterySystem


class BatterySystemLimitsTest(unittest.TestCase):
    def setUp(self) -> None:
        battery_modules = list()
        self.battery_system = BatterySystem(battery_modules)

    def test_ok_voltage1(self):
        voltage = 500
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertFalse(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_ok_voltage2(self):
        voltage = 596
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertFalse(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_ok_current1(self):
        voltage = 0
        current = 15.0
        self.battery_system.update_measurements(voltage, current)
        self.assertFalse(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_ok_current2(self):
        voltage = 0
        current = 29
        self.battery_system.update_measurements(voltage, current)
        self.assertFalse(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_voltage_lower1(self):
        voltage = 459
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_lower2(self):
        voltage = 434
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_upper1(self):
        voltage = 598
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_upper2(self):
        voltage = 603
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_current_upper1(self):
        voltage = 0
        current = 30.5
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_upper2(self):
        voltage = 0
        current = 31.5
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_lower1(self):
        voltage = 0
        current = -30.5
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_lower2(self):
        voltage = 0
        current = -31.5
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_critical_voltage_upper1(self):
        voltage = 605
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_upper2(self):
        voltage = 700
        current = 0
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_lower1(self):
        voltage = 0
        current = 400
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_lower2(self):
        voltage = 0
        current = 300
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_current_upper1(self):
        voltage = 0
        current = 33
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_upper2(self):
        voltage = 0
        current = 40
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_lower1(self):
        voltage = 0
        current = -33
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_lower2(self):
        voltage = 0
        current = -40
        self.battery_system.update_measurements(voltage, current)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())


if __name__ == '__main__':
    unittest.main()
