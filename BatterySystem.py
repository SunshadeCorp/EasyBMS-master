from typing import List

from BatteryModule import BatteryModule


class BatterySystem:
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 403.2  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 604.8  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 460.8  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 597.6  # V

    LOWER_CURRENT_LIMIT_WARNING: float = -30  # A
    UPPER_CURRENT_LIMIT_WARNING: float = 30  # A
    LOWER_CURRENT_LIMIT_CRITICAL: float = -32  # A
    UPPER_CURRENT_LIMIT_CRITICAL: float = 32  # A

    def __init__(self, battery_modules: List[BatteryModule]) -> None:
        # Uninitialized values
        self.voltage: float = 0
        self.current: float = 0

        self.is_initialized = False
        self.battery_modules: list = battery_modules

    def update_measurements(self, voltage: float, current: float) -> None:
        self.voltage = voltage
        self.current = current
        self.is_initialized = True

        if self.has_critical_voltage():
            pass
        elif self.has_warning_voltage():
            pass

        if self.has_critical_current():
            pass
        elif self.has_warning_current():
            pass

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_CRITICAL or self.voltage > self.UPPER_VOLTAGE_LIMIT_CRITICAL

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_WARNING or self.voltage > self.UPPER_VOLTAGE_LIMIT_WARNING

    def has_critical_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_CRITICAL or self.current > self.UPPER_CURRENT_LIMIT_CRITICAL

    def has_warning_current(self) -> bool:
        return self.current < self.LOWER_CURRENT_LIMIT_WARNING or self.current > self.UPPER_CURRENT_LIMIT_WARNING

    def get_soc(self) -> float:
        soc_sum: float = 0

        for module in self.battery_modules:
            soc_sum += module.get_soc()

        return soc_sum / len(self.battery_modules)

    def get_highest_cell_temp(self) -> float:
        # todo
        pass

    def get_lowest_cell_temp(self) -> float:
        # todo
        pass

    def get_highest_cell_voltage(self) -> float:
        # todo
        pass

    def get_highest_voltage_cells(self) -> float:
        # todo
        pass
