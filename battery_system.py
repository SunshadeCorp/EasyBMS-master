from typing import List

from battery_cell import BatteryCell
from battery_module import BatteryModule
from measurement_event import MeasurementEvent


class BatterySystem:
    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -10000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 10000  # V
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 432.0  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 604.8  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 460.8  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 597.6  # V

    LOWER_CURRENT_LIMIT_IMPLAUSIBLE: float = -500  # A
    UPPER_CURRENT_LIMIT_IMPLAUSIBLE: float = 500  # A
    LOWER_CURRENT_LIMIT_CRITICAL: float = -32  # A
    UPPER_CURRENT_LIMIT_CRITICAL: float = 32  # A
    LOWER_CURRENT_LIMIT_WARNING: float = -30  # A
    UPPER_CURRENT_LIMIT_WARNING: float = 30  # A

    def __init__(self, number_of_modules: int) -> None:
        assert 1 <= number_of_modules <= 12

        # Uninitialized values
        self.voltage: float = 0
        self.current: float = 0

        self.is_initialized = False

        # Events
        self.current_event = MeasurementEvent()
        self.voltage_event = MeasurementEvent()

        self.battery_modules: List[BatteryModule] = []
        for module_id in range(0, number_of_modules):
            module = BatteryModule(module_id)
            self.battery_modules.append(module)

    def update_measurements(self, voltage: float, current: float) -> None:
        self.voltage = voltage
        self.current = current
        self.is_initialized = True

        if self.has_implausible_voltage():
            self.voltage_event.on_implausible(self)
        elif self.has_critical_voltage():
            self.voltage_event.on_critical(self)
        elif self.has_warning_voltage():
            self.voltage_event.on_warning(self)

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
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_CRITICAL or self.voltage > self.UPPER_VOLTAGE_LIMIT_CRITICAL

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_WARNING or self.voltage > self.UPPER_VOLTAGE_LIMIT_WARNING

    def has_implausible_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_IMPLAUSIBLE \
               or self.current > self.UPPER_CURRENT_LIMIT_IMPLAUSIBLE

    def has_critical_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_CRITICAL or self.current > self.UPPER_CURRENT_LIMIT_CRITICAL

    def has_warning_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_WARNING or self.current > self.UPPER_CURRENT_LIMIT_WARNING

    def get_soc(self) -> float:
        soc_sum: float = 0

        for module in self.battery_modules:
            soc_sum += module.get_soc()

        return soc_sum / len(self.battery_modules)

    def get_cells(self) -> List[BatteryCell]:
        cell_list: List[BatteryCell] = []

        for module in self.battery_modules:
            for cell in module.cells:
                cell_list.append(cell)

        return cell_list

    def get_highest_cell_temp(self) -> float:
        sorted_modules = sorted(self.battery_modules, key=lambda x: x.temp(), reverse=True)
        return sorted_modules[0]

    def get_lowest_module_temp(self) -> float:
        sorted_modules = sorted(self.battery_modules, key=lambda x: x.temp())
        return sorted_modules[0].temp()

    def get_highest_cell_voltage(self) -> float:
        cell_list = self.get_cells()
        cell_list.sort(key=lambda x: x.voltage, reverse=True)
        return cell_list[0].voltage

    def get_highest_voltage_cells(self, number) -> List[BatteryCell]:
        cell_list = self.get_cells()
        cell_list.sort(key=lambda x: x.voltage, reverse=True)
        return cell_list[0:(number - 1)]
