from battery_cell import BatteryCell
from battery_system import BatterySystem
from heartbeat_event import HeartbeatEvent
from battery_module import BatteryModule


class BatteryManager:
    def __init__(self, battery_system: BatterySystem) -> None:
        self.battery_system: BatterySystem = battery_system

        # Register battery system event handlers
        self.battery_system.voltage_event.on_critical += self.on_critical_battery_system_voltage
        self.battery_system.voltage_event.on_warning += self.on_battery_system_voltage_warning
        self.battery_system.voltage_event.on_implausible += self.on_implausible_battery_system_voltage

        self.battery_system.current_event.on_critical += self.on_critical_battery_system_current
        self.battery_system.current_event.on_warning += self.on_battery_system_current_warning
        self.battery_system.current_event.on_implausible += self.on_implausible_battery_system_current

        # Register battery module event handlers
        for module in self.battery_system.battery_modules:
            module.heartbeat_event.on_heartbeat_missed += self.on_heartbeat_missed

            module.module_temp_event.on_critical += self.on_critical_module_temperature
            module.module_temp_event.on_warning += self.on_module_temperature_warning
            module.module_temp_event.on_implausible += self.on_implausible_module_temperature

            module.chip_temp_event.on_critical += self.on_critical_chip_temperature
            module.chip_temp_event.on_warning += self.on_chip_temperature_warning
            module.chip_temp_event.on_implausible += self.on_implausible_chip_temperature

            module.voltage_event.on_critical += self.on_critical_module_voltage
            module.voltage_event.on_warning += self.on_module_voltage_warning
            module.voltage_event.on_implausible += self.on_implausible_module_voltage

            for cell in module.cells:
                cell.voltage_event.on_critical += self.on_critical_cell_voltage
                cell.voltage_event.on_warning += self.on_cell_voltage_warning
                cell.voltage_event.on_implausible += self.on_implausible_cell_voltage

    def balance(self) -> None:
        highest_cells = self.battery_system.get_highest_voltage_cells(5)
        '''
        for cell in highest_cells:
            cell.start_balance_discharge()
        '''
        # todo only balance for 5-10 seconds
        print("TODO: implement balancing algorithm")

    def trigger_safety_disconnect(self) -> None:
        print("TODO: implement safety disconnect")

    # Event handling for critical events

    def on_critical_battery_system_voltage(self, system: BatterySystem) -> None:
        print(f'[CRITICAL] battery system voltage: {self.battery_system.voltage}V')
        self.trigger_safety_disconnect()

    def on_critical_battery_system_current(self, system: BatterySystem) -> None:
        print(f'[CRITICAL] battery system current: {self.battery_system.current}A')
        self.trigger_safety_disconnect()

    def on_critical_module_temperature(self, module: BatteryModule) -> None:
        print(f'[CRITICAL] module temperature on module {module.id}: {module.module_temp1}°C, {module.module_temp2}°C')
        self.trigger_safety_disconnect()

    def on_critical_chip_temperature(self, module: BatteryModule) -> None:
        print(f'[CRITICAL] chip temperature on module {module.id}: {module.chip_temp}°C')
        self.trigger_safety_disconnect()

    def on_critical_module_voltage(self, module: BatteryModule) -> None:
        print(f'[CRITICAL] module voltage on module {module.id}: {module.voltage}V')  #
        self.trigger_safety_disconnect()

    def on_critical_cell_voltage(self, cell: BatteryCell) -> None:
        print(f'[CRITICAL] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}')
        self.trigger_safety_disconnect()

    # Event handling for warning events

    def on_battery_system_current_warning(self, system: BatterySystem) -> None:
        print(f'[WARNING] battery system voltage: {self.battery_system.voltage}V')

    def on_battery_system_voltage_warning(self, system: BatterySystem) -> None:
        print(f'[WARNING] battery system current: {self.battery_system.current}A')

    def on_module_temperature_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] module temperature on module {module.id}: {module.module_temp1}°C, {module.module_temp2}°C')

    def on_chip_temperature_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] chip temperature on module {module.id}: {module.chip_temp}°C')

    def on_module_voltage_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] module voltage on module {module.id}: {module.voltage}V')

    def on_cell_voltage_warning(self, cell: BatteryCell) -> None:
        print(f'[WARNING] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}')

    # Event handling for implausible values
    # Todo: implement loud failing for development time
    # notify user of implausible state and shut off the system

    def on_implausible_battery_system_voltage(self, system: BatterySystem) -> None:
        print(f'[IMPLAUSIBLE] battery system voltage: {self.battery_system.voltage}V')
        self.trigger_safety_disconnect()

    def on_implausible_battery_system_current(self, system: BatterySystem) -> None:
        print(f'[IMPLAUSIBLE] battery system current: {self.battery_system.current}A')
        self.trigger_safety_disconnect()

    def on_implausible_module_temperature(self, module: BatteryModule) -> None:
        print(
            f'[IMPLAUSIBLE] module temperature on module {module.id}: {module.module_temp1}°C, {module.module_temp2}°C')
        self.trigger_safety_disconnect()

    def on_implausible_chip_temperature(self, module: BatteryModule) -> None:
        print(f'[IMPLAUSIBLE] chip temperature on module {module.id}: {module.chip_temp}°C')
        self.trigger_safety_disconnect()

    def on_implausible_module_voltage(self, module: BatteryModule) -> None:
        print(f'[IMPLAUSIBLE] module voltage on module {module.id}: {module.voltage}V')
        self.trigger_safety_disconnect()

    def on_implausible_cell_voltage(self, cell: BatteryCell) -> None:
        print(f'[IMPLAUSIBLE] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}')
        self.trigger_safety_disconnect()

    # Other event handlers

    def on_heartbeat_missed(self, esp_number: int) -> None:
        print(f'Heartbeat missed on esp: {esp_number})')
