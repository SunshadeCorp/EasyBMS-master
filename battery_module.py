import time
from typing import List

from battery_cell import BatteryCell
from heartbeat_event import HeartbeatEvent
from measurement_event import MeasurementEvent


class BatteryModule:
    LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE: float = -100.0  # °C
    UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE: float = 500.0  # °C
    LOWER_MODULE_TEMP_LIMIT_CRITICAL: float = -20.0  # °C
    UPPER_MODULE_TEMP_LIMIT_CRITICAL: float = 50.0  # °C
    LOWER_MODULE_TEMP_LIMIT_WARNING: float = -10.0  # °C
    UPPER_MODULE_TEMP_LIMIT_WARNING: float = 45.0  # °C

    LOWER_CHIP_TEMP_LIMIT_IMPLAUSIBLE: float = -100.0  # °C
    UPPER_CHIP_TEMP_LIMIT_IMPLAUSIBLE: float = 500.0  # °C
    LOWER_CHIP_TEMP_LIMIT_CRITICAL: float = -40.0  # °C
    UPPER_CHIP_TEMP_LIMIT_CRITICAL: float = 80.0  # °C
    LOWER_CHIP_TEMP_LIMIT_WARNING: float = -30.0  # °C
    UPPER_CHIP_TEMP_LIMIT_WARNING: float = 60.0  # °C

    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -1000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 1000  # V
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 36.0  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 50.4  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 38.4  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 49.8  # V

    ESP_TIMEOUT: float = 5.000  # Seconds

    def __init__(self, module_id: int) -> None:
        # Uninitialized
        self.voltage: float = None
        self.module_temp1: float = None
        self.module_temp2: float = None
        self.chip_temp: float = None
        self.last_esp_uptime: int = None
        self.last_esp_uptime_in_own_time: float = None

        self.id = module_id
        self.keep_monitoring_heartbeats: bool = True

        # Events
        self.module_temp_event = MeasurementEvent()
        self.chip_temp_event = MeasurementEvent()
        self.voltage_event = MeasurementEvent()
        self.heartbeat_event = HeartbeatEvent()

        self.cells: List[BatteryCell] = []
        for i in range(0, 12):
            new_cell = BatteryCell(i, self.id)
            self.cells.append(new_cell)

    def heartbeat_monitor_thread(self):
        while self.keep_monitoring_heartbeats:
            own_time: float = time.time()

            if self.last_esp_uptime_in_own_time - own_time > self.ESP_TIMEOUT:
                self.heartbeat_event.on_heartbeat_missed()
            time.sleep(1000)

    def temp(self) -> float:
        return (self.module_temp1 + self.module_temp2) / 2.0

    def soc(self) -> float:
        soc_sum: float = 0

        for cell in self.cells:
            soc_sum += cell.get_soc()

        return soc_sum / len(self.cells)

    def update_module_temps(self, temp1: float, temp2: float) -> None:
        self.module_temp1 = temp1
        self.module_temp2 = temp2

        if self.has_implausible_module_temp():
            self.module_temp_event.on_implausible(self)
        elif self.has_critical_module_temp():
            self.module_temp_event.on_critical(self)
        elif self.has_warning_module_temp():
            self.module_temp_event.on_warning(self)

    def update_module_voltage(self, module_voltage: float) -> None:
        self.voltage = module_voltage

        if self.has_implausible_voltage():
            self.voltage_event.on_implausible(self)
        elif self.has_critical_voltage():
            self.voltage_event.on_critical(self)
        elif self.has_warning_voltage():
            self.voltage_event.on_warning(self)

    def update_chip_temp(self, chip_temp: float) -> None:
        self.chip_temp = chip_temp

        if self.has_implausible_chip_temp():
            self.chip_temp_event.on_implausible(self)
        elif self.has_critical_chip_temp():
            self.chip_temp_event.on_critical(self)
        elif self.has_warning_chip_temp():
            self.chip_temp_event.on_warning(self)

    def update_esp_uptime(self, esp_uptime: int) -> None:
        self.last_esp_uptime = esp_uptime
        self.heartbeat_event.on_heartbeat()

    def has_warning_module_temp1(self) -> bool:
        return self.module_temp1 < self.LOWER_MODULE_TEMP_LIMIT_WARNING \
               or self.module_temp1 > self.UPPER_MODULE_TEMP_LIMIT_WARNING

    def has_critical_module_temp1(self) -> bool:
        return self.module_temp1 < self.LOWER_MODULE_TEMP_LIMIT_CRITICAL \
               or self.module_temp1 > self.UPPER_MODULE_TEMP_LIMIT_CRITICAL

    def has_implausible_module_temp1(self) -> bool:
        return self.module_temp1 < self.LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE \
               or self.module_temp1 > self.UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE

    def has_warning_module_temp2(self) -> bool:
        return self.module_temp2 < self.LOWER_MODULE_TEMP_LIMIT_WARNING \
               or self.module_temp2 > self.UPPER_MODULE_TEMP_LIMIT_WARNING

    def has_critical_module_temp2(self) -> bool:
        return self.module_temp2 < self.LOWER_MODULE_TEMP_LIMIT_CRITICAL \
               or self.module_temp2 > self.UPPER_MODULE_TEMP_LIMIT_CRITICAL

    def has_implausible_module_temp2(self) -> bool:
        return self.module_temp2 < self.LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE \
               or self.module_temp2 > self.UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE

    def has_critical_module_temp(self) -> bool:
        return self.has_critical_module_temp1() or self.has_critical_module_temp2()

    def has_warning_module_temp(self) -> bool:
        return self.has_warning_module_temp1() or self.has_warning_module_temp2()

    def has_implausible_module_temp(self) -> bool:
        return self.has_implausible_module_temp1() or self.has_implausible_module_temp2()

    def has_critical_chip_temp(self) -> bool:
        return self.chip_temp < self.LOWER_CHIP_TEMP_LIMIT_CRITICAL \
               or self.chip_temp > self.UPPER_CHIP_TEMP_LIMIT_CRITICAL

    def has_warning_chip_temp(self) -> bool:
        return self.chip_temp < self.LOWER_CHIP_TEMP_LIMIT_WARNING \
               or self.chip_temp > self.UPPER_CHIP_TEMP_LIMIT_WARNING

    def has_implausible_chip_temp(self) -> bool:
        return self.chip_temp < self.LOWER_CHIP_TEMP_LIMIT_IMPLAUSIBLE \
               or self.chip_temp > self.UPPER_CHIP_TEMP_LIMIT_IMPLAUSIBLE

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_CRITICAL or self.voltage > self.UPPER_VOLTAGE_LIMIT_CRITICAL

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_WARNING or self.voltage > self.UPPER_VOLTAGE_LIMIT_WARNING

    def has_implausible_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE \
               or self.voltage > self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE
