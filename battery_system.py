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

        self.lower_voltage_limit_warning: float = number_of_modules * BatteryModule.LOWER_VOLTAGE_LIMIT_WARNING
        self.upper_voltage_limit_warning: float = number_of_modules * BatteryModule.UPPER_VOLTAGE_LIMIT_WARNING
        self.lower_voltage_limit_critical: float = number_of_modules * BatteryModule.LOWER_VOLTAGE_LIMIT_CRITICAL
        self.upper_voltage_limit_critical: float = number_of_modules * BatteryModule.UPPER_VOLTAGE_LIMIT_CRITICAL

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
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE \
               or self.voltage > self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.lower_voltage_limit_critical or self.voltage > self.upper_voltage_limit_critical

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.lower_voltage_limit_warning or self.voltage > self.upper_voltage_limit_warning

    def has_implausible_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_IMPLAUSIBLE \
               or self.current > self.UPPER_CURRENT_LIMIT_IMPLAUSIBLE

    def has_critical_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_CRITICAL or self.current > self.UPPER_CURRENT_LIMIT_CRITICAL

    def has_warning_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_WARNING or self.current > self.UPPER_CURRENT_LIMIT_WARNING

    def calculated_voltage(self) -> float:
        return sum(cell.voltage for cell in self.cells())

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

    def highest_cell_temp(self) -> float:
        sorted_modules = sorted(self.battery_modules, key=lambda x: x.temp(), reverse=True)
        return sorted_modules[0].temp()

    def lowest_module_temp(self) -> float:
        sorted_modules = sorted(self.battery_modules, key=lambda x: x.temp())
        return sorted_modules[0].temp()

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
