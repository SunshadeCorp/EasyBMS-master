import time
from typing import List

from battery_cell import BatteryCell
from battery_cell_list import BatteryCellList
from battery_module import BatteryModule
from measurement import MeasurementLimits
from measurement import Measurement


class BatterySystem:
    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -2000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 2000  # V

    LOWER_CURRENT_LIMIT_IMPLAUSIBLE: float = -500  # A
    UPPER_CURRENT_LIMIT_IMPLAUSIBLE: float = 500  # A
    LOWER_CURRENT_LIMIT_CRITICAL: float = -32  # A
    UPPER_CURRENT_LIMIT_CRITICAL: float = 32  # A
    LOWER_CURRENT_LIMIT_WARNING: float = -30  # A
    UPPER_CURRENT_LIMIT_WARNING: float = 30  # A

    current_limits = MeasurementLimits()
    current_limits.critical_lower = LOWER_CURRENT_LIMIT_CRITICAL
    current_limits.critical_upper = UPPER_CURRENT_LIMIT_CRITICAL
    current_limits.implausible_lower = LOWER_CURRENT_LIMIT_IMPLAUSIBLE
    current_limits.implausible_upper = UPPER_CURRENT_LIMIT_IMPLAUSIBLE
    current_limits.warning_lower = LOWER_CURRENT_LIMIT_WARNING
    current_limits.warning_upper = UPPER_CURRENT_LIMIT_WARNING

    SLIDING_WINDOW_TIME: float = 180.0  # seconds

    def __init__(self, number_of_modules: int, number_of_serial_cells: int) -> None:
        assert 1 <= number_of_modules <= 16

        cells_total = number_of_modules * number_of_serial_cells
        self.voltage_limits = MeasurementLimits()
        self.voltage_limits.implausible_lower = self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE
        self.voltage_limits.implausible_upper = self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE
        self.voltage_limits.critical_lower = cells_total * BatteryCell.LOWER_VOLTAGE_LIMIT_CRITICAL
        self.voltage_limits.critical_upper = cells_total * BatteryCell.UPPER_VOLTAGE_LIMIT_CRITICAL
        self.voltage_limits.warning_lower = cells_total * BatteryCell.LOWER_VOLTAGE_LIMIT_WARNING
        self.voltage_limits.warning_upper = cells_total * BatteryCell.UPPER_VOLTAGE_LIMIT_WARNING

        self.voltage: Measurement = Measurement(self, self.voltage_limits)
        self.current: Measurement = Measurement(self, self.current_limits)

        self.battery_modules: List[BatteryModule] = []
        for module_id in range(0, number_of_modules):
            module = BatteryModule(module_id, number_of_serial_cells)
            self.battery_modules.append(module)

        self.sliding_window_soc_values = []

    def __str__(self):
        modules_string = ''
        for battery_module in self.battery_modules:
            cells_string = ''
            for cell in battery_module.cells:
                try:
                    cells_string += (f'{cell.voltage.value:.3f}' + ('+' if cell.balance_pin_state else '')).ljust(7)
                except TypeError:
                    cells_string += (f'{cell.voltage.value}' + ('' if cell.balance_pin_state is None else 'N')).ljust(7)
            try:
                modules_string += f'{battery_module.voltage.value:.2f}V'.ljust(7) \
                                  + f'{battery_module.module_temp1.value:.1f}°C'.ljust(7) \
                                  + f'{battery_module.module_temp2.value:.1f}°C'.ljust(7) \
                                  + f'{cells_string}\n'
            except TypeError:
                modules_string += f'{battery_module.voltage.value}V'.ljust(7) \
                                  + f'{battery_module.module_temp1.value}°C'.ljust(7) \
                                  + f'{battery_module.module_temp2.value}°C'.ljust(7) \
                                  + f'{cells_string}\n'
        try:
            return f'System: {self.voltage.value:.2f}V {self.current.value:.2f}A ' \
                   f'calculated: {self.calculated_voltage():.2f}V Modules:\n{modules_string}'
        except TypeError:
            return f'System: {self.voltage.value}V {self.current.value}A Modules:\n{modules_string}'

    def check_heartbeats(self):
        for battery_module in self.battery_modules:
            battery_module.check_heartbeat()

    def load_adjusted_calculated_voltage(self) -> float:
        return sum(cell.load_adjusted_voltage(self.current.value) for cell in self.cells())

    def calculated_voltage(self) -> float:
        return sum(cell.voltage.value for cell in self.cells())

    def temp(self) -> float:
        return sum(battery_modules.temp() for battery_modules in self.battery_modules) / len(self.battery_modules)

    def sliding_window_soc(self) -> float:
        self.sliding_window_soc_values.append((time.time(), self.load_adjusted_soc()))
        while self.sliding_window_soc_values[0][0] + self.SLIDING_WINDOW_TIME < time.time():
            self.sliding_window_soc_values.pop(0)
        return sum(soc_value[1] for soc_value in self.sliding_window_soc_values) / len(self.sliding_window_soc_values)

    def load_adjusted_soc(self) -> float:
        return sum(module.load_adjusted_soc(self.current.value) for module in self.battery_modules) \
            / len(self.battery_modules)

    def soc(self) -> float:
        return sum(module.soc() for module in self.battery_modules) / len(self.battery_modules)

    def cells(self) -> BatteryCellList:
        return BatteryCellList([cell for module in self.battery_modules for cell in module.cells])

    def lowest_module_temp(self) -> float:
        return min(battery_modules.min_temp() for battery_modules in self.battery_modules)

    def highest_module_temp(self) -> float:
        return max(battery_modules.max_temp() for battery_modules in self.battery_modules)

    def highest_voltage_cells(self, number) -> List[BatteryCell]:
        cell_list = self.cells()
        cell_list.sort(key=lambda x: x.voltage.value, reverse=True)
        return cell_list[0:number]
