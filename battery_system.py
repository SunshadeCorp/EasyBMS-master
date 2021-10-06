from typing import List

from battery_cell import BatteryCell
from battery_module import BatteryModule
from measurement_event import MeasurementEvent


class BatterySystem:
    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -10000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 10000  # V

    LOWER_CURRENT_LIMIT_IMPLAUSIBLE: float = -500  # A
    UPPER_CURRENT_LIMIT_IMPLAUSIBLE: float = 500  # A
    LOWER_CURRENT_LIMIT_CRITICAL: float = -32  # A
    UPPER_CURRENT_LIMIT_CRITICAL: float = 32  # A
    LOWER_CURRENT_LIMIT_WARNING: float = -30  # A
    UPPER_CURRENT_LIMIT_WARNING: float = 30  # A

    def __init__(self, number_of_modules: int) -> None:
        assert 1 <= number_of_modules <= 12

        # Uninitialized values
        self.voltage: float or None = None
        self.current: float or None = None

        self.lower_voltage_limit_critical: float = number_of_modules * BatteryModule.LOWER_VOLTAGE_LIMIT_CRITICAL
        self.upper_voltage_limit_critical: float = number_of_modules * BatteryModule.UPPER_VOLTAGE_LIMIT_CRITICAL
        self.lower_voltage_limit_warning: float = number_of_modules * BatteryModule.LOWER_VOLTAGE_LIMIT_WARNING
        self.upper_voltage_limit_warning: float = number_of_modules * BatteryModule.UPPER_VOLTAGE_LIMIT_WARNING

        # Events
        self.current_event = MeasurementEvent()
        self.voltage_event = MeasurementEvent()

        self.battery_modules: List[BatteryModule] = []
        for module_id in range(0, number_of_modules):
            module = BatteryModule(module_id)
            self.battery_modules.append(module)

    def __str__(self):
        modules_string = ''
        for battery_module in self.battery_modules:
            cells_string = ''
            for cell in battery_module.cells:
                try:
                    cells_string += (f'{cell.voltage:.2f}' + ('+' if cell.balance_pin_state else '')).ljust(7)
                except TypeError:
                    cells_string += (f'{cell.voltage}' + ('' if cell.balance_pin_state is None else 'N')).ljust(7)
            try:
                modules_string += f'{battery_module.voltage:.2f}V'.ljust(7) \
                                  + f'{battery_module.module_temp1:.1f}°C'.ljust(7) \
                                  + f'{battery_module.module_temp2:.1f}°C'.ljust(7) \
                                  + f'{cells_string}\n'
            except TypeError:
                modules_string += f'{battery_module.voltage}V'.ljust(7) \
                                  + f'{battery_module.module_temp1}°C'.ljust(7) \
                                  + f'{battery_module.module_temp2}°C'.ljust(7) \
                                  + f'{cells_string}\n'
        try:
            return f'System: {self.voltage:.2f}V {self.current:.2f}A ' \
                   f'calculated: {self.calculated_voltage():.2f}V Modules:\n{modules_string}'
        except TypeError:
            return f'System: {self.voltage}V {self.current}A Modules:\n{modules_string}'

    def check_heartbeats(self):
        for battery_module in self.battery_modules:
            battery_module.check_heartbeat()

    def update_voltage(self, voltage: float) -> None:
        self.voltage = voltage

        if self.has_implausible_voltage():
            self.voltage_event.on_implausible(self)
        elif self.has_critical_voltage():
            self.voltage_event.on_critical(self)
        elif self.has_warning_voltage():
            self.voltage_event.on_warning(self)

    def update_current(self, current: float) -> None:
        self.current = current

        if self.has_implausible_current():
            self.current_event.on_implausible(self)
        elif self.has_critical_current():
            self.current_event.on_critical(self)
        elif self.has_warning_current():
            self.current_event.on_warning(self)

    def has_implausible_voltage(self) -> bool:
        return not (self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE <= self.voltage <= self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE)

    def has_critical_voltage(self) -> bool:
        return not (self.lower_voltage_limit_critical <= self.voltage <= self.upper_voltage_limit_critical)

    def has_warning_voltage(self) -> bool:
        return not (self.lower_voltage_limit_warning <= self.voltage <= self.upper_voltage_limit_warning)

    def has_implausible_current(self) -> bool:
        return not (self.LOWER_CURRENT_LIMIT_IMPLAUSIBLE <= self.current <= self.UPPER_CURRENT_LIMIT_IMPLAUSIBLE)

    def has_critical_current(self) -> bool:
        return not (self.LOWER_CURRENT_LIMIT_CRITICAL <= self.current <= self.UPPER_CURRENT_LIMIT_CRITICAL)

    def has_warning_current(self) -> bool:
        return not (self.LOWER_CURRENT_LIMIT_WARNING <= self.current <= self.UPPER_CURRENT_LIMIT_WARNING)

    def calculated_voltage(self) -> float:
        return sum(cell.voltage for cell in self.cells())

    def temp(self) -> float:
        return sum(battery_modules.temp() for battery_modules in self.battery_modules) / len(self.battery_modules)

    def soc(self) -> float:
        soc_sum: float = 0

        for module in self.battery_modules:
            soc_sum += module.soc()

        return soc_sum / len(self.battery_modules)

    def cells(self) -> List[BatteryCell]:
        cell_list: List[BatteryCell] = []

        for module in self.battery_modules:
            for cell in module.cells:
                cell_list.append(cell)

        return cell_list

    def lowest_module_temp(self) -> float:
        return min(battery_modules.min_temp() for battery_modules in self.battery_modules)

    def highest_module_temp(self) -> float:
        return max(battery_modules.max_temp() for battery_modules in self.battery_modules)

    def highest_cell_voltage(self) -> float:
        cell_list = self.cells()
        cell_list.sort(key=lambda x: x.voltage, reverse=True)
        return cell_list[0].voltage

    def lowest_cell_voltage(self) -> float:
        cell_list = self.cells()
        cell_list.sort(key=lambda x: x.voltage, reverse=False)
        return cell_list[0].voltage

    def highest_voltage_cells(self, number) -> List[BatteryCell]:
        cell_list = self.cells()
        cell_list.sort(key=lambda x: x.voltage, reverse=True)
        return cell_list[0:(number - 1)]

    def is_in_relax_time(self) -> bool:
        for cell in self.cells():
            if cell.is_relaxing():
                return True
        return False

    def is_currently_balancing(self) -> bool:
        for cell in self.cells():
            if cell.is_balance_discharging():
                return True
        return False
