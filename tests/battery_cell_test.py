import unittest
import unittest.mock
from unittest.mock import MagicMock

from battery_cell import BatteryCell


class BatteryCellTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cell_id = 1
        self.module_id = 2
        self.cell = BatteryCell(self.cell_id, self.module_id)

    def test_init(self):
        self.assertEqual(self.cell.id, self.cell_id)
        self.assertEqual(self.cell.module_id, self.module_id)
        self.assertEqual(self.cell.voltage, None)
        self.assertEqual(self.cell.balance_pin_state, False)
        self.assertEqual(self.cell.last_discharge_time, 0)

    def test_load_adjusted_voltage(self):
        voltage = 2.0  # V
        self.cell.update_voltage(voltage)
        current = 5.0  # A

        load_adjusted = self.cell.load_adjusted_voltage(current)
        self.assertAlmostEqual(load_adjusted, voltage + BatteryCell.INTERNAL_IMPEDANCE*current)

    def test_load_adjusted_soc(self):
        voltage = 3.5  # V
        self.cell.update_voltage(voltage)
        current = 10.0  # A

        soc = self.cell.soc()
        adjusted_soc = self.cell.load_adjusted_soc(current)

        self.assertTrue(adjusted_soc > soc)
        self.assertTrue(0.0 <= soc <= 1.0)
        self.assertTrue(0.0 <= adjusted_soc <= 1.0)

    def test_soc(self):
        voltage = 3.869  # V
        expected_soc = 0.75
        self.cell.update_voltage(voltage)
        self.assertAlmostEqual(self.cell.soc(), expected_soc)

        voltage = 3.628  # V
        expected_soc = 0.35
        self.cell.update_voltage(voltage)
        self.assertAlmostEqual(self.cell.soc(), expected_soc)

    def test_has_implausible_voltage(self):
        self.cell.update_voltage(-4.0)  # V
        self.assertTrue(self.cell.has_implausible_voltage())
        self.cell.update_voltage(-2.0)  # V
        self.assertTrue(self.cell.has_implausible_voltage())

        self.cell.update_voltage(3.5)  # V
        self.assertFalse(self.cell.has_implausible_voltage())
        self.cell.update_voltage(7.0)  # V
        self.assertFalse(self.cell.has_implausible_voltage())

        self.cell.update_voltage(50.0)  # V
        self.assertTrue(self.cell.has_implausible_voltage())

    def test_has_critical_voltage(self):
        self.cell.update_voltage(-1.0)  # V
        self.assertTrue(self.cell.has_critical_voltage())
        self.cell.update_voltage(0.0)  # V
        self.assertTrue(self.cell.has_critical_voltage())
        self.cell.update_voltage(2.0)  # V
        self.assertTrue(self.cell.has_critical_voltage())

        self.cell.update_voltage(3.62)  # V
        self.assertFalse(self.cell.has_critical_voltage())
        self.cell.update_voltage(3.86)  # V
        self.assertFalse(self.cell.has_critical_voltage())

        self.cell.update_voltage(4.5)  # V
        self.assertTrue(self.cell.has_critical_voltage())

    def test_has_warning_voltage(self):
        self.cell.update_voltage(-1.0)  # V
        self.assertTrue(self.cell.has_warning_voltage())
        self.cell.update_voltage(0.0)  # V
        self.assertTrue(self.cell.has_warning_voltage())
        self.cell.update_voltage(2.0)  # V
        self.assertTrue(self.cell.has_warning_voltage())
        self.cell.update_voltage(3.1)  # V
        self.assertTrue(self.cell.has_warning_voltage())

        self.cell.update_voltage(3.62)  # V
        self.assertFalse(self.cell.has_warning_voltage())
        self.cell.update_voltage(3.86)  # V
        self.assertFalse(self.cell.has_warning_voltage())

        self.cell.update_voltage(4.18)  # V
        self.assertTrue(self.cell.has_warning_voltage())
        self.cell.update_voltage(4.50)  # V
        self.assertTrue(self.cell.has_warning_voltage())

    def test_update_voltage(self):
        for voltage in [-1.0, 0.0, 1.0, 2.234, 3.4, 3.5, 8.0]:
            self.cell.update_voltage(voltage)
            self.assertEqual(self.cell.voltage, voltage)

    def test_relax_time(self):
        self.assertGreaterEqual(BatteryCell.RELAX_TIME, 1.0)  # seconds
        self.assertLessEqual(BatteryCell.RELAX_TIME, 120.0)  # seconds

    @unittest.mock.patch('time.time', return_value=120.0)
    def test_is_relaxing(self, mock_time: MagicMock):
        self.cell.last_discharge_time = 120.0 - (BatteryCell.RELAX_TIME * (1.0 / 3.0))  # seconds
        self.assertTrue(self.cell.is_relaxing())
        mock_time.assert_called()

        self.cell.last_discharge_time = 120.0 - (BatteryCell.RELAX_TIME * (2.0 / 3.0))  # seconds
        self.assertTrue(self.cell.is_relaxing())
        mock_time.assert_called()

        self.cell.last_discharge_time = 120.0 - (BatteryCell.RELAX_TIME * (4.0 / 3.0))  # seconds
        self.assertFalse(self.cell.is_relaxing())
        mock_time.assert_called()

    def test_start_balance_discharge(self):
        balance_time = 60

        handler_called = False

        mod_num = 0
        cell_num = 0
        b_time = 0

        def handler(a, b, c):
            nonlocal handler_called
            nonlocal mod_num
            nonlocal cell_num
            nonlocal b_time
            handler_called = True
            mod_num = a
            cell_num = b
            b_time = c

        self.cell.communication_event.send_balance_request += handler

        self.assertFalse(self.cell.is_balance_discharging())
        self.cell.start_balance_discharge(balance_time)  # seconds
        self.assertTrue(self.cell.is_balance_discharging())
        self.assertTrue(handler_called)
        self.assertEqual(mod_num, self.cell.module_id)
        self.assertEqual(cell_num, self.cell_id)
        self.assertEqual(b_time, balance_time)

    @unittest.mock.patch('time.time', return_value=120.0)
    def test_on_balance_discharged_stopped(self, mock_time: MagicMock):
        # Test call when not balancing
        self.cell.last_discharge_time = 0.0
        self.cell.balance_pin_state = False
        self.cell.on_balance_discharged_stopped()
        self.assertEqual(self.cell.last_discharge_time, 0.0)
        self.assertFalse(self.cell.is_balance_discharging())

        # Test Start balancing
        def handler(a, b, c):
            pass

        self.cell.communication_event.send_balance_request += handler
        self.cell.start_balance_discharge(60.0)
        self.assertEqual(self.cell.last_discharge_time, 0.0)
        self.assertTrue(self.cell.is_balance_discharging())

        # Test stop balancing
        self.cell.on_balance_discharged_stopped()
        self.assertFalse(self.cell.is_balance_discharging())
        self.assertEqual(self.cell.last_discharge_time, 120.0)

    def test_is_balance_discharging(self):
        self.cell.balance_pin_state = False
        self.assertEqual(self.cell.is_balance_discharging(), False)
        self.cell.balance_pin_state = True
        self.assertEqual(self.cell.is_balance_discharging(), True)


if __name__ == '__main__':
    unittest.main()
