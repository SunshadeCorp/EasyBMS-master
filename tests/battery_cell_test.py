import unittest
import time
import unittest.mock
from unittest.mock import MagicMock

from battery_cell import BatteryCell


class BatteryCellTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_init(self):
        cell = BatteryCell(1, 2)
        self.assertEqual(cell.id, 1)
        self.assertEqual(cell.module_id, 2)
        self.assertEqual(cell.voltage, None)
        self.assertEqual(cell.balance_pin_state, False)
        self.assertEqual(cell.last_discharge_time, 0)

    def test_load_adjusted_voltage(self):
        cell = BatteryCell(1, 2)
        voltage = 2.0  # V
        cell.update_voltage(voltage)
        current = 5.0  # A

        load_adjusted = cell.load_adjusted_voltage(current)
        self.assertAlmostEqual(load_adjusted, voltage + BatteryCell.INTERNAL_IMPEDANCE*current)

    def test_load_adjusted_soc(self):
        cell = BatteryCell(1, 2)
        voltage = 3.5  # V
        cell.update_voltage(voltage)
        current = 10.0  # A

        soc = cell.soc()
        adjusted_soc = cell.load_adjusted_soc(current)

        self.assertTrue(adjusted_soc > soc)
        self.assertTrue(0.0 <= soc <= 1.0)
        self.assertTrue(0.0 <= adjusted_soc <= 1.0)

    def test_soc(self):
        cell = BatteryCell(1, 2)

        voltage = 3.869  # V
        expected_soc = 0.75
        cell.update_voltage(voltage)
        self.assertAlmostEqual(cell.soc(), expected_soc)

        voltage = 3.628  # V
        expected_soc = 0.35
        cell.update_voltage(voltage)
        self.assertAlmostEqual(cell.soc(), expected_soc)

    def test_has_implausible_voltage(self):
        cell = BatteryCell(1, 2)

        cell.update_voltage(-4.0)  # V
        self.assertTrue(cell.has_implausible_voltage())
        cell.update_voltage(-2.0)  # V
        self.assertTrue(cell.has_implausible_voltage())

        cell.update_voltage(3.5)  # V
        self.assertFalse(cell.has_implausible_voltage())
        cell.update_voltage(7.0)  # V
        self.assertFalse(cell.has_implausible_voltage())

        cell.update_voltage(50.0)  # V
        self.assertTrue(cell.has_implausible_voltage())

    def test_has_critical_voltage(self):
        cell = BatteryCell(1, 2)

        cell.update_voltage(-1.0)  # V
        self.assertTrue(cell.has_critical_voltage())
        cell.update_voltage(0.0)  # V
        self.assertTrue(cell.has_critical_voltage())
        cell.update_voltage(2.0)  # V
        self.assertTrue(cell.has_critical_voltage())

        cell.update_voltage(3.62)  # V
        self.assertFalse(cell.has_critical_voltage())
        cell.update_voltage(3.86)  # V
        self.assertFalse(cell.has_critical_voltage())

        cell.update_voltage(4.5)  # V
        self.assertTrue(cell.has_critical_voltage())

    def test_has_warning_voltage(self):
        cell = BatteryCell(1, 2)

        cell.update_voltage(-1.0)  # V
        self.assertTrue(cell.has_warning_voltage())
        cell.update_voltage(0.0)  # V
        self.assertTrue(cell.has_warning_voltage())
        cell.update_voltage(2.0)  # V
        self.assertTrue(cell.has_warning_voltage())
        cell.update_voltage(3.1)  # V
        self.assertTrue(cell.has_warning_voltage())

        cell.update_voltage(3.62)  # V
        self.assertFalse(cell.has_warning_voltage())
        cell.update_voltage(3.86)  # V
        self.assertFalse(cell.has_warning_voltage())

        cell.update_voltage(4.18)  # V
        self.assertTrue(cell.has_warning_voltage())
        cell.update_voltage(4.50)  # V
        self.assertTrue(cell.has_warning_voltage())

    def test_update_voltage(self):
        cell = BatteryCell(1, 2)

        for voltage in [-1.0, 0.0, 1.0, 2.234, 3.4, 3.5, 8.0]:
            cell.update_voltage(voltage)
            self.assertEqual(cell.voltage, voltage)

    @unittest.mock.patch('time.time', return_value=120.0)
    def test_is_relaxing(self, mock_time: MagicMock):
        cell = BatteryCell(1, 2)

        cell.last_discharge_time = 120.0 - 10.0  # seconds
        self.assertTrue(cell.is_relaxing())
        mock_time.assert_called()

        cell.last_discharge_time = 120.0 - 60.0  # seconds
        self.assertTrue(cell.is_relaxing())
        mock_time.assert_called()

        cell.last_discharge_time = 120.0 - 100.0  # seconds
        self.assertFalse(cell.is_relaxing())
        mock_time.assert_called()

    def test_start_balance_discharge(self):
        cell_id = 1
        module_id = 2
        cell = BatteryCell(cell_id, module_id)
        balance_time = 60

        handler_called = False

        def handler(a, b, c):
            nonlocal handler_called
            handler_called = True
            print("called")

        cell.communication_event.send_balance_request += handler

        self.assertFalse(cell.balance_pin_state)
        cell.start_balance_discharge(balance_time)  # seconds
        self.assertTrue(cell.balance_pin_state)
        self.assertTrue(handler_called)

    def test_on_balance_discharged_stopped(self):
        pass

    def test_is_balance_discharging(self):
        pass


if __name__ == '__main__':
    unittest.main()
