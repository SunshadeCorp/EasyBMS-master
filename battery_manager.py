from battery_cell import BatteryCell
from battery_system import BatterySystem
from heartbeat_event import HeartbeatEvent
from battery_module import BatteryModule
from main import EasyBMSMaster


class BatteryManager:
    MIN_CELL_DIFF_FOR_BALANCING: float = 0.010  # V
    MAX_CELL_DIFF_FOR_BALANCING: float = 0.5  # V
    BALANCE_DISCHARGE_TIME: float = 5.0  # Seconds
    BALANCE_RELAX_TIME: float = 60  # Seconds

    def __init__(self, battery_system: BatterySystem, slave_communicator: EasyBMSMaster) -> None:
        self.battery_system: BatterySystem = battery_system
        self.slave_communicator: EasyBMSMaster = slave_communicator

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
            module.heartbeat_event.on_heartbeat += self.on_heartbeat

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

    def is_in_emergency_state(self) -> bool:
        print('[NOT IMPLEMENTED] BatteryManager:is_in_emergency_state()')
        return False

    def balance(self) -> None:
        if self.battery_system.is_in_relax_time() or self.battery_system.is_currently_balancing():
            return

        if self.is_in_emergency_state():
            print('[WARNING] System is in emergency state and will not perform balancing.')
            return

        highest_voltage = self.battery_system.highest_cell_voltage()
        lowest_voltage = self.battery_system.lowest_cell_voltage()

        if highest_voltage - lowest_voltage < self.MIN_CELL_DIFF_FOR_BALANCING:
            return

        if highest_voltage - lowest_voltage > self.MAX_CELL_DIFF_FOR_BALANCING:
            print('[WARNING] Difference in cell voltages is too high for balancing.'
                  'The system will not perform balancing')
            return

        highest_cells = self.battery_system.highest_voltage_cells(5)

        for cell in highest_cells:
            cell.start_balance_discharge(self.BALANCE_DISCHARGE_TIME)

        # Cells are now discharging until the BMS slave resets the balance pins

    def trigger_safety_disconnect(self) -> None:
        # todo: retry several times to ensure message delivery
        self.slave_communicator.open_battery_relays()

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
        print(f'[CRITICAL] module voltage on module {module.id}: {module.voltage}V')
        self.trigger_safety_disconnect()

    def on_critical_cell_voltage(self, cell: BatteryCell) -> None:
        print(f'[CRITICAL] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}V')
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
        print(f'[WARNING] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}V')

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
        print(f'[IMPLAUSIBLE] cell voltage on module {cell.module_id}, cell {cell.id}: {cell.voltage}V')
        self.trigger_safety_disconnect()

    # Other event handlers

    def on_heartbeat_missed(self, module: BatteryModule) -> None:
        print(f'Heartbeat missed on module: {module.id})')

    def on_heartbeat(self, module: BatteryModule) -> None:
        print(f'Got heartbeat on module: {module.id}')
