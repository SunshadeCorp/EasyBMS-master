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

    ESP_TIMEOUT: float = 5.000  # Seconds

    def __init__(self, module_id: int, number_of_serial_cells: int) -> None:
        # Uninitialized
        self.voltage: float or None = None
        self.module_temp1: float or None = None
        self.module_temp2: float or None = None
        self.chip_temp: float or None = None
        self.last_esp_uptime: int or None = None
        self.last_esp_uptime_in_own_time: float or None = None

        self.id = module_id
        self.keep_monitoring_heartbeats: bool = True
        self.last_accurate_reading_request_time: float = 0

        # Events
        self.module_temp_event = MeasurementEvent()
        self.chip_temp_event = MeasurementEvent()
        self.voltage_event = MeasurementEvent()
        self.heartbeat_event = HeartbeatEvent()

        self.cells: List[BatteryCell] = []
        for i in range(0, number_of_serial_cells):
            new_cell = BatteryCell(i, self.id)
            self.cells.append(new_cell)

        self.lower_voltage_limit_critical: float = number_of_serial_cells * BatteryCell.LOWER_VOLTAGE_LIMIT_CRITICAL
        self.upper_voltage_limit_critical: float = number_of_serial_cells * BatteryCell.UPPER_VOLTAGE_LIMIT_CRITICAL
        self.lower_voltage_limit_warning: float = number_of_serial_cells * BatteryCell.LOWER_VOLTAGE_LIMIT_WARNING
        self.upper_voltage_limit_warning: float = number_of_serial_cells * BatteryCell.UPPER_VOLTAGE_LIMIT_WARNING

    def __str__(self):
        cell_numbers_string = ''
        cell_voltages_string = ''
        cell_balancings_string = ''
        for cell in self.cells:
            cell_numbers_string += f'{cell.id:02d}'.ljust(7)
            cell_voltages_string += f'{cell.voltage:.2f}'.ljust(7)
            cell_balancings_string += f'{cell.balance_pin_state}'.ljust(7)
        cells_string = f'{cell_numbers_string}\n{cell_voltages_string}\n{cell_balancings_string}\n'
        return f'Module {self.id}: {self.voltage:.2f}V ' \
               f'{self.module_temp1}°C {self.module_temp2}°C Cells:\n{cells_string}'

    def check_heartbeat(self):
        if self.last_esp_uptime_in_own_time is None:
            print(f'ESP-Module {self.id} last uptime not initialized!')
            return
        own_time: float = time.time()
        if own_time - self.last_esp_uptime_in_own_time > self.ESP_TIMEOUT:
            self.heartbeat_event.on_heartbeat_missed(self)

    def heartbeat_monitor_thread(self):
        while self.keep_monitoring_heartbeats:
            self.check_heartbeat()
            time.sleep(1000)

    def temp(self) -> float:
        return (self.module_temp1 + self.module_temp2) / 2.0

    def min_temp(self) -> float:
        return min(self.module_temp1, self.module_temp2)

    def max_temp(self) -> float:
        return max(self.module_temp1, self.module_temp2)

    def load_adjusted_soc(self, current: float) -> float:
        return sum(cell.load_adjusted_soc(current) for cell in self.cells) / len(self.cells)

    def soc(self) -> float:
        return sum(cell.soc() for cell in self.cells) / len(self.cells)

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
        self.last_esp_uptime_in_own_time = time.time()
        self.heartbeat_event.on_heartbeat(self)

    def has_implausible_module_temp1(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE <= self.module_temp1
                    <= self.UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE)

    def has_critical_module_temp1(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_CRITICAL <= self.module_temp1 <= self.UPPER_MODULE_TEMP_LIMIT_CRITICAL)

    def has_warning_module_temp1(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_WARNING <= self.module_temp1 <= self.UPPER_MODULE_TEMP_LIMIT_WARNING)

    def has_implausible_module_temp2(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE <= self.module_temp2
                    <= self.UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE)

    def has_critical_module_temp2(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_CRITICAL <= self.module_temp2 <= self.UPPER_MODULE_TEMP_LIMIT_CRITICAL)

    def has_warning_module_temp2(self) -> bool:
        return not (self.LOWER_MODULE_TEMP_LIMIT_WARNING <= self.module_temp2 <= self.UPPER_MODULE_TEMP_LIMIT_WARNING)

    def has_implausible_module_temp(self) -> bool:
        return self.has_implausible_module_temp1() or self.has_implausible_module_temp2()

    def has_critical_module_temp(self) -> bool:
        return self.has_critical_module_temp1() or self.has_critical_module_temp2()

    def has_warning_module_temp(self) -> bool:
        return self.has_warning_module_temp1() or self.has_warning_module_temp2()

    def has_implausible_chip_temp(self) -> bool:
        return not (self.LOWER_CHIP_TEMP_LIMIT_IMPLAUSIBLE <= self.chip_temp <= self.UPPER_CHIP_TEMP_LIMIT_IMPLAUSIBLE)

    def has_critical_chip_temp(self) -> bool:
        return not (self.LOWER_CHIP_TEMP_LIMIT_CRITICAL <= self.chip_temp <= self.UPPER_CHIP_TEMP_LIMIT_CRITICAL)

    def has_warning_chip_temp(self) -> bool:
        return not (self.LOWER_CHIP_TEMP_LIMIT_WARNING <= self.chip_temp <= self.UPPER_CHIP_TEMP_LIMIT_WARNING)

    def has_implausible_voltage(self) -> bool:
        return not (self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE <= self.voltage <= self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE)

    def has_critical_voltage(self) -> bool:
        return not (self.lower_voltage_limit_critical <= self.voltage <= self.upper_voltage_limit_critical)

    def has_warning_voltage(self) -> bool:
        return not (self.lower_voltage_limit_warning <= self.voltage <= self.upper_voltage_limit_warning)

    def min_voltage_cell(self) -> BatteryCell:
        return min(self.cells, key=lambda x: x.voltage)

    def max_voltage_cell(self) -> BatteryCell:
        return max(self.cells, key=lambda x: x.voltage)
