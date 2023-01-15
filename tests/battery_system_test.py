import unittest

import sys
sys.path.insert(0,'..')

from battery_system import BatterySystem

class BatterySystemTest(unittest.TestCase):
    def setUp(self) -> None:
        number_of_modules = 12
        number_of_cells = 12
        self.battery_system = BatterySystem(number_of_modules, number_of_cells)

    def test_ok_voltage1(self):
        voltage = 500
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertFalse(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_ok_voltage2(self):
        voltage = 596
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertFalse(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_ok_current1(self):
        voltage = 0
        current = 15.0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertFalse(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_ok_current2(self):
        voltage = 0
        current = 29
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertFalse(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_voltage_lower1(self):
        voltage = 459
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_lower2(self):
        voltage = 434
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_upper1(self):
        voltage = 598
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_voltage_upper2(self):
        voltage = 603
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertFalse(self.battery_system.has_critical_voltage())

    def test_warning_current_upper1(self):
        voltage = 0
        current = 30.5
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_upper2(self):
        voltage = 0
        current = 31.5
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_lower1(self):
        voltage = 0
        current = -30.5
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_warning_current_lower2(self):
        voltage = 0
        current = -31.5
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertFalse(self.battery_system.has_critical_current())

    def test_critical_voltage_upper1(self):
        voltage = 605
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_upper2(self):
        voltage = 700
        current = 0
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_lower1(self):
        voltage = 0
        current = 400
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_voltage_lower2(self):
        voltage = 0
        current = 300
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_voltage())
        self.assertTrue(self.battery_system.has_critical_voltage())

    def test_critical_current_upper1(self):
        voltage = 0
        current = 33
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_upper2(self):
        voltage = 0
        current = 40
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_lower1(self):
        voltage = 0
        current = -33
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())

    def test_critical_current_lower2(self):
        voltage = 0
        current = -40
        self.battery_system.update_current(current)
        self.battery_system.update_voltage(voltage)
        self.assertTrue(self.battery_system.has_warning_current())
        self.assertTrue(self.battery_system.has_critical_current())


if __name__ == '__main__':
    unittest.main()
