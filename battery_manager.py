import time

from battery_cell import BatteryCell
from battery_cell_list import BatteryCellList
from battery_system import BatterySystem
# from heartbeat_event import HeartbeatEvent
from battery_module import BatteryModule
from battery_system_balancer import BatterySystemBalancer
from slave_communicator import SlaveCommunicator


class BatteryManager:
    ESP_TIMEOUT_WARNING_SECONDS: int = 60
    ESP_TIMEOUT_CRITICAL_SECONDS: int = 120 * 60

    def __init__(self, battery_system: BatterySystem, slave_communicator: SlaveCommunicator) -> None:
        self.battery_system: BatterySystem = battery_system
        self.slave_communicator: SlaveCommunicator = slave_communicator

        self.balancer = BatterySystemBalancer(battery_system, slave_communicator)

        # Register battery system event handlers
        self.battery_system.voltage.event.on_critical += self.on_critical_battery_system_voltage
        self.battery_system.voltage.event.on_warning += self.on_battery_system_voltage_warning
        self.battery_system.voltage.event.on_implausible += self.on_implausible_battery_system_voltage

        self.battery_system.current.event.on_critical += self.on_critical_battery_system_current
        self.battery_system.current.event.on_warning += self.on_battery_system_current_warning
        self.battery_system.current.event.on_implausible += self.on_implausible_battery_system_current

        # Register battery module event handlers
        for module in self.battery_system.battery_modules:
            module.heartbeat_event.on_heartbeat_missed += self.on_heartbeat_missed
            module.heartbeat_event.on_heartbeat += self.on_heartbeat

            module.module_temp1.event.on_critical += self.on_critical_module_temperature
            module.module_temp1.event.on_warning += self.on_module_temperature_warning
            module.module_temp1.event.on_implausible += self.on_implausible_module_temperature

            module.module_temp2.event.on_critical += self.on_critical_module_temperature
            module.module_temp2.event.on_warning += self.on_module_temperature_warning
            module.module_temp2.event.on_implausible += self.on_implausible_module_temperature

            module.chip_temp.event.on_critical += self.on_critical_chip_temperature
            module.chip_temp.event.on_warning += self.on_chip_temperature_warning
            module.chip_temp.event.on_implausible += self.on_implausible_chip_temperature

            module.voltage.event.on_critical += self.on_critical_module_voltage
            module.voltage.event.on_warning += self.on_module_voltage_warning
            module.voltage.event.on_implausible += self.on_implausible_module_voltage

            for cell in module.cells:
                cell.voltage.event.on_critical += self.on_critical_cell_voltage
                cell.voltage.event.on_warning += self.on_cell_voltage_warning
                cell.voltage.event.on_implausible += self.on_implausible_cell_voltage

    def balance(self) -> None:
        self.balancer.balance()

    def set_limits(self):
        cells: BatteryCellList = self.battery_system.cells()
        lowest_voltage: float = cells.lowest_voltage()
        highest_voltage: float = cells.highest_voltage()
        if lowest_voltage <= BatteryCell.soc_to_voltage(0.15):
            self.slave_communicator.send_discharge_limit(False)
        elif lowest_voltage >= BatteryCell.soc_to_voltage(0.18):
            self.slave_communicator.send_discharge_limit(True)
        if highest_voltage >= BatteryCell.soc_to_voltage(0.93):
            self.slave_communicator.send_charge_limit(False)
        elif highest_voltage <= BatteryCell.soc_to_voltage(0.90):
            self.slave_communicator.send_charge_limit(True)

    def check_cell_voltage_times(self):
        timeout_cells = self.battery_system.cells().with_voltage_older_than(self.ESP_TIMEOUT_CRITICAL_SECONDS)
        if len(timeout_cells) > 0:
            message = f'[CRITICAL] following cells got no update: {time.time()}\n'
            message += '\n'.join([f'Module{cell.module_id} Cell{cell.id}: {cell.last_voltage_time}' for cell in timeout_cells])
            print(message, flush=True) 
            self.trigger_safety_disconnect(message)
            return
        
        timeout_cells = self.battery_system.cells().with_voltage_older_than(self.ESP_TIMEOUT_WARNING_SECONDS)
        if len(timeout_cells) > 0:
            message = f'[WARNING] following cells got no update: {time.time()}\n'
            message += '\n'.join([f'Module{cell.module_id} Cell{cell.id}: {cell.last_voltage_time}' for cell in timeout_cells])
            print(message, flush=True) 
            

    def trigger_safety_disconnect(self, reason: str) -> None:
        self.slave_communicator.open_battery_relays(reason)

    # Event handling for critical events
    def on_critical_battery_system_voltage(self, system: BatterySystem) -> None:
        message = f'[CRITICAL] battery system voltage: {system.voltage.value}V'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_critical_battery_system_current(self, system: BatterySystem) -> None:
        message = f'[CRITICAL] battery system current: {system.current.value}A'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_critical_module_temperature(self, module: BatteryModule) -> None:
        message = f'[CRITICAL] module temperature on module {module.id}: {module.module_temp1.value}°C, {module.module_temp2.value}°C'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_critical_chip_temperature(self, module: BatteryModule) -> None:
        message = f'[CRITICAL] chip temperature on module {module.id}: {module.chip_temp.value}°C'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_critical_module_voltage(self, module: BatteryModule) -> None:
        message = f'[CRITICAL] module voltage on module {module.id}: {module.voltage.value}V'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_critical_cell_voltage(self, cell: BatteryCell) -> None:
        message = f'[CRITICAL] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage.value}V'
        print(message, flush=True)
        if cell.critical_counter > 4:
            self.trigger_safety_disconnect(message)

    # Event handling for warning events

    def on_battery_system_current_warning(self, system: BatterySystem) -> None:
        print(f'[WARNING] battery system voltage: {system.voltage.value}V')

    def on_battery_system_voltage_warning(self, system: BatterySystem) -> None:
        print(f'[WARNING] battery system current: {system.current.value}A')

    def on_module_temperature_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] module temperature on module {module.id}: {module.module_temp1.value}°C, {module.module_temp2.value}°C')

    def on_chip_temperature_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] chip temperature on module {module.id}: {module.chip_temp.value}°C')

    def on_module_voltage_warning(self, module: BatteryModule) -> None:
        print(f'[WARNING] module voltage on module {module.id}: {module.voltage.value}V')

    def on_cell_voltage_warning(self, cell: BatteryCell) -> None:
        print(f'[WARNING] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage.value}V')

    # Event handling for implausible values
    # notify user of implausible state and shut off the system

    def on_implausible_battery_system_voltage(self, system: BatterySystem) -> None:
        message = f'[IMPLAUSIBLE] battery system voltage: {system.voltage.value}V'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_implausible_battery_system_current(self, system: BatterySystem) -> None:
        message = f'[IMPLAUSIBLE] battery system current: {system.current.value}A'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_implausible_module_temperature(self, module: BatteryModule) -> None:
        message = f'[IMPLAUSIBLE] module temperature on module {module.id}: {module.module_temp1.value}°C, {module.module_temp2.value}°C'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_implausible_chip_temperature(self, module: BatteryModule) -> None:
        message = f'[IMPLAUSIBLE] chip temperature on module {module.id}: {module.chip_temp.value}°C'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_implausible_module_voltage(self, module: BatteryModule) -> None:
        message = f'[IMPLAUSIBLE] module voltage on module {module.id}: {module.voltage.value}V'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    def on_implausible_cell_voltage(self, cell: BatteryCell) -> None:
        message = f'[IMPLAUSIBLE] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage.value}V'
        print(message, flush=True)
        self.trigger_safety_disconnect(message)

    # Other event handlers

    def on_heartbeat_missed(self, module: BatteryModule) -> None:
        print(f'Heartbeat missed on module: {module.id})')

    def on_heartbeat(self, module: BatteryModule) -> None:
        # print(f'Got heartbeat on module: {module.id}')
        pass
