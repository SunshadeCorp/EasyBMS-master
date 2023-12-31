import time
from typing import List

from battery_cell import BatteryCell
from heartbeat_event import HeartbeatEvent
from measurement import MeasurementEvent
from measurement import MeasurementLimits
from measurement import Measurement


class BatteryModule:
    LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE: float = -100.0  # °C
    UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE: float = 500.0  # °C
    LOWER_MODULE_TEMP_LIMIT_CRITICAL: float = -20.0  # °C
    UPPER_MODULE_TEMP_LIMIT_CRITICAL: float = 50.0  # °C
    LOWER_MODULE_TEMP_LIMIT_WARNING: float = -10.0  # °C
    UPPER_MODULE_TEMP_LIMIT_WARNING: float = 45.0  # °C

    module_temp_limits = MeasurementLimits()
    module_temp_limits.critical_lower = LOWER_MODULE_TEMP_LIMIT_CRITICAL
    module_temp_limits.critical_upper = UPPER_MODULE_TEMP_LIMIT_CRITICAL
    module_temp_limits.implausible_lower = LOWER_MODULE_TEMP_LIMIT_IMPLAUSIBLE
    module_temp_limits.implausible_upper = UPPER_MODULE_TEMP_LIMIT_IMPLAUSIBLE
    module_temp_limits.warning_lower = LOWER_MODULE_TEMP_LIMIT_WARNING
    module_temp_limits.warning_upper = UPPER_MODULE_TEMP_LIMIT_WARNING

    LOWER_CHIP_TEMP_LIMIT_IMPLAUSIBLE: float = -100.0  # °C
    UPPER_CHIP_TEMP_LIMIT_IMPLAUSIBLE: float = 500.0  # °C
    LOWER_CHIP_TEMP_LIMIT_CRITICAL: float = -40.0  # °C
    UPPER_CHIP_TEMP_LIMIT_CRITICAL: float = 80.0  # °C
    LOWER_CHIP_TEMP_LIMIT_WARNING: float = -30.0  # °C
    UPPER_CHIP_TEMP_LIMIT_WARNING: float = 60.0  # °C

    chip_temp_limits = MeasurementLimits()
    chip_temp_limits.critical_lower = LOWER_CHIP_TEMP_LIMIT_CRITICAL
    chip_temp_limits.critical_upper = UPPER_CHIP_TEMP_LIMIT_CRITICAL
    chip_temp_limits.implausible_lower = LOWER_CHIP_TEMP_LIMIT_IMPLAUSIBLE
    chip_temp_limits.implausible_upper = UPPER_CHIP_TEMP_LIMIT_IMPLAUSIBLE
    chip_temp_limits.warning_lower = LOWER_CHIP_TEMP_LIMIT_WARNING
    chip_temp_limits.warning_upper = UPPER_CHIP_TEMP_LIMIT_WARNING

    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -1000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 1000  # V

    ESP_TIMEOUT: float = 20.000  # Seconds

    def __init__(self, module_id: int, number_of_serial_cells: int) -> None:
        self.voltage_limits = MeasurementLimits()
        self.voltage_limits.implausible_lower = self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE
        self.voltage_limits.implausible_upper = self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE
        self.voltage_limits.critical_lower = number_of_serial_cells * BatteryCell.LOWER_VOLTAGE_LIMIT_CRITICAL
        self.voltage_limits.critical_upper = number_of_serial_cells * BatteryCell.UPPER_VOLTAGE_LIMIT_CRITICAL
        self.voltage_limits.warning_lower = number_of_serial_cells * BatteryCell.LOWER_VOLTAGE_LIMIT_WARNING
        self.voltage_limits.warning_upper = number_of_serial_cells * BatteryCell.UPPER_VOLTAGE_LIMIT_WARNING
        self.voltage: Measurement = Measurement(self.voltage_limits)
        self.module_temp1: Measurement = Measurement(self.module_temp_limits)
        self.module_temp2: Measurement = Measurement(self.module_temp_limits)
        self.chip_temp: Measurement = Measurement(self.chip_temp_limits)

        # Uninitialized

        self.last_esp_uptime: int or None = None
        self.last_esp_uptime_in_own_time: float or None = None

        self.id = module_id
        self.keep_monitoring_heartbeats: bool = True
        self.last_accurate_reading_request_time: float = 0

        # Events
        self.heartbeat_event = HeartbeatEvent()

        self.cells: List[BatteryCell] = []
        for i in range(0, number_of_serial_cells):
            new_cell = BatteryCell(i, self.id)
            self.cells.append(new_cell)

    def __str__(self):
        cell_numbers_string = ''
        cell_voltages_string = ''
        cell_balancings_string = ''
        for cell in self.cells:
            cell_numbers_string += f'{cell.id:02d}'.ljust(7)
            cell_voltages_string += f'{cell.voltage.value:.2f}'.ljust(7)
            cell_balancings_string += f'{cell.balance_pin_state}'.ljust(7)
        cells_string = f'{cell_numbers_string}\n{cell_voltages_string}\n{cell_balancings_string}\n'
        return f'Module {self.id}: {self.voltage.value:.2f}V ' \
               f'{self.module_temp1.value}°C {self.module_temp2.value}°C Cells:\n{cells_string}'

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
        return (self.module_temp1.value + self.module_temp2.value) / 2.0

    def min_temp(self) -> float:
        return min(self.module_temp1.value, self.module_temp2.value)

    def max_temp(self) -> float:
        return max(self.module_temp1.value, self.module_temp2.value)

    def load_adjusted_soc(self, current: float) -> float:
        return sum(cell.load_adjusted_soc(current) for cell in self.cells) / len(self.cells)

    def soc(self) -> float:
        return sum(cell.soc() for cell in self.cells) / len(self.cells)

    def update_esp_uptime(self, esp_uptime: int) -> None:
        self.last_esp_uptime = esp_uptime
        self.last_esp_uptime_in_own_time = time.time()
        self.heartbeat_event.on_heartbeat(self)

    def min_voltage_cell(self) -> BatteryCell:
        return min(self.cells, key=lambda x: x.voltage)

    def max_voltage_cell(self) -> BatteryCell:
        return max(self.cells, key=lambda x: x.voltage)
