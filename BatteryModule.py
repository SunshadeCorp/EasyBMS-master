from typing import List

from BatteryCell import BatteryCell


class BatteryModule:
    LOWER_MODULE_TEMP_LIMIT = -10  # °C
    UPPER_MODULE_TEMP_LIMIT = 50  # °C
    LOWER_CHIP_TEMP_LIMIT = -20  # °C
    UPPER_CHIP_TEMP_LIMIT = 60  # °C
    LOWER_VOLTAGE_LIMIT = 33.6  # V
    UPPER_VOLTAGE_LIMIT = 50.4  # V

    def __init__(self):
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

    def trigger_missed_heartbeat_event(self):
        # todo
        pass

    def trigger_critical_temperature_event(self):
        # todo
        pass

    def trigger_implausible_temperature_event(self):
        # todo
        pass

    def trigger_critical_module_voltage_event(self):
        # todo
        pass

    def trigger_implausible_module_voltage_event(self):
        # todo
        pass
