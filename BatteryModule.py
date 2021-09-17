from typing import List

from BatteryCell import BatteryCell


class BatteryModule:
    LOWER_MODULE_TEMP_LIMIT_CRITICAL: float = -20.0  # °C
    UPPER_MODULE_TEMP_LIMIT_CRITICAL: float = 50.0  # °C
    LOWER_MODULE_TEMP_LIMIT_WARNING: float = -10.0  # °C
    UPPER_MODULE_TEMP_LIMIT_WARNING: float = 45.0  # °C

    LOWER_CHIP_TEMP_LIMIT_CRITICAL: float = -40.0  # °C
    UPPER_CHIP_TEMP_LIMIT_CRITICAL: float = 80.0  # °C
    LOWER_CHIP_TEMP_LIMIT_WARNING: float = -30.0  # °C
    UPPER_CHIP_TEMP_LIMIT_WARNING: float = 60.0  # °C

    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 33.6  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 50.4  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 38.4  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 49.8  # V

    def __init__(self) -> None:
        self.cells: List[BatteryCell] = None
        self.voltage: float = None
        self.module_temp1: float = None
        self.module_temp2: float = None
        self.chip_temp: float = None
        self.heartbeat_timestamp: int = None

    def get_soc(self) -> float:
        soc_sum: float = 0

        for cell in self.cells:
            soc_sum += cell.get_soc()

        return soc_sum / len(self.cells)

    def update_measurements(self, temp1: float, temp2: float, voltage, chip_temp) -> None:
        self.module_temp1 = temp1
        self.module_temp2 = temp2
        self.voltage = voltage
        self.chip_temp = chip_temp

        # todo
        if self.has_critical_module_temp():
            pass
        elif self.has_warning_module_temp():
            pass

        if self.has_critical_chip_temp():
            pass
        elif self.has_warning_chip_temp():
            pass

        if self.has_critical_voltage():
            pass
        elif self.has_warning_voltage():
            pass

    def has_warning_module_temp1(self) -> bool:
        return self.module_temp1 < self.LOWER_MODULE_TEMP_LIMIT_WARNING \
               or self.module_temp1 > self.UPPER_MODULE_TEMP_LIMIT_WARNING

    def has_warning_module_temp2(self) -> bool:
        return self.module_temp2 < self.LOWER_MODULE_TEMP_LIMIT_WARNING \
               or self.module_temp2 > self.UPPER_MODULE_TEMP_LIMIT_WARNING

    def has_critical_module_temp1(self) -> bool:
        return self.module_temp1 < self.LOWER_MODULE_TEMP_LIMIT_CRITICAL \
               or self.module_temp1 > self.UPPER_MODULE_TEMP_LIMIT_CRITICAL

    def has_critical_module_temp2(self) -> bool:
        return self.module_temp2 < self.LOWER_MODULE_TEMP_LIMIT_CRITICAL \
               or self.module_temp2 > self.UPPER_MODULE_TEMP_LIMIT_CRITICAL

    def has_critical_module_temp(self) -> bool:
        return self.has_critical_module_temp1() or self.has_critical_module_temp2()

    def has_warning_module_temp(self) -> bool:
        return self.has_warning_module_temp1() or self.has_warning_module_temp2()

    def has_critical_chip_temp(self) -> bool:
        return self.chip_temp < self.LOWER_CHIP_TEMP_LIMIT_CRITICAL \
               or self.chip_temp > self.UPPER_CHIP_TEMP_LIMIT_CRITICAL

    def has_warning_chip_temp(self) -> bool:
        return self.chip_temp < self.LOWER_CHIP_TEMP_LIMIT_WARNING \
               or self.chip_temp > self.UPPER_CHIP_TEMP_LIMIT_WARNING

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_CRITICAL or self.voltage > self.UPPER_VOLTAGE_LIMIT_CRITICAL

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_WARNING or self.voltage > self.UPPER_VOLTAGE_LIMIT_WARNING

    def trigger_missed_heartbeat_event(self) -> None:
        # todo
        pass

    def trigger_critical_temperature_event(self) -> None:
        # todo
        pass

    def trigger_implausible_temperature_event(self) -> None:
        # todo
        pass

    def trigger_critical_module_voltage_event(self) -> None:
        # todo
        pass

    def trigger_implausible_module_voltage_event(self) -> None:
        # todo
        pass
