import unittest
import unittest.mock
from unittest.mock import MagicMock

from battery_manager import BatteryManager
from battery_system import BatterySystem

class BatteryManagerTest(unittest.TestCase):
    def setUp(self):
        self.modules = 8
        self.cells = 12
        battery_system = BatterySystem(self.modules, self.cells)
        self.battery_manager = BatteryManager(battery_system, None)

    def test_init(self):
        battery_system = self.battery_manager.battery_system

        self.assertEqual(len(battery_system.voltage_event.on_critical), 1)
        self.assertEqual(len(battery_system.voltage_event.on_warning), 1)
        self.assertEqual(len(battery_system.voltage_event.on_implausible), 1)

        for module in battery_system.battery_modules:
            self.assertEqual(len(module.heartbeat_event.on_heartbeat_missed), 1)
            self.assertEqual(len(module.heartbeat_event.on_heartbeat), 1)

            self.assertEqual(len(module.module_temp_event.on_critical), 1)
            self.assertEqual(len(module.module_temp_event.on_warning), 1)
            self.assertEqual(len(module.module_temp_event.on_implausible), 1)

            self.assertEqual(len(module.chip_temp_event.on_critical), 1)
            self.assertEqual(len(module.chip_temp_event.on_warning), 1)
            self.assertEqual(len(module.chip_temp_event.on_implausible), 1)

            self.assertEqual(len(module.voltage_event.on_critical), 1)
            self.assertEqual(len(module.voltage_event.on_warning), 1)
            self.assertEqual(len(module.voltage_event.on_implausible), 1)

            for cell in module.cells:
                self.assertEqual(len(cell.voltage_event.on_critical), 1)
                self.assertEqual(len(cell.voltage_event.on_warning), 1)
                self.assertEqual(len(cell.voltage_event.on_implausible), 1)

    def test_balance(self):
        # Test 0: balancing constants
        assert BatteryManager.BALANCE_DISCHARGE_TIME > 0.0
        assert 0.0 < BatteryManager.MIN_CELL_DIFF_FOR_BALANCING \
                    < BatteryManager.MAX_CELL_DIFF_FOR_BALANCING

        # Test 1: no new balancing while already balancing

        # Test 2: no balancing while relaxing

        # Test 3: no balancing when diff not high enough

        # Test 4: no balancing when system is balanced

        # Test 4: low cells should be balanced

    def test_trigger_safety_disconnect(self):
        pass

    def test_on_critical_battery_system_voltage(self):
        pass

    def test_on_critical_battery_system_current(self):
        pass

    def test_on_critical_module_temperature(self):
        pass

    def test_on_critical_chip_temperature(self):
        pass

    def test_on_critical_module_voltage(self):
        pass

    def test_on_critical_cell_voltage(self):
        pass

    def test_on_battery_system_current_warning(self):
        pass

    def test_on_battery_system_voltage_warning(self):
        pass

    def test_on_module_temperature_warning(self):
        pass

    def test_on_chip_temperature_warning(self):
        pass

    def test_on_module_voltage_warning(self):
        pass

    def test_on_cell_voltage_warning(self):
        pass

    def test_on_implausible_battery_system_voltage(self):
        pass

    def test_on_implausible_battery_system_current(self):
        pass

    def test_on_implausible_module_temperature(self):
        pass

    def test_on_implausible_chip_temperature(self):
        pass

    def test_on_implausible_module_voltage(self):
        pass

    def test_on_implausible_cell_voltage(self):
        pass

    def test_on_heartbeat_missed(self):
        pass

    def test_on_heartbeat(self):
        pass

if __name__ == '__main__':
    unittest.main()