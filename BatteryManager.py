from BatterySystem import BatterySystem
from HeartbeatEvent import HeartbeatEvent
from BatteryModule import BatteryModule


class BatteryManager:
    battery_system = None

    def __init__(self, battery_system: BatterySystem) -> None:
        self.battery_system = battery_system

        # Register battery system event handlers
        self.battery_system.voltage_event.on_critical += self.on_critical_battery_system_voltage
        self.battery_system.voltage_event.on_warning += self.on_battery_system_voltage_warning
        self.battery_system.current_event.on_critical += self.on_critical_battery_system_current
        self.battery_system.current_event.on_warning += self.on_battery_system_current_warning

        # Register battery module event handlers
        for module in self.battery_system.battery_modules:
            module.heartbeat_event.on_heartbeat_missed += self.on_heartbeat_missed

            module.module_temp_event.on_critical += self.on_critical_module_temperature
            module.module_temp_event.on_warning += self.on_module_temperature_warning

            module.chip_temp_event.on_critical += self.on_critical_chip_temperature
            module.chip_temp_event.on_warning += self.on_chip_temperature_warning

            module.voltage_event.on_critical += self.on_critical_module_voltage
            module.voltage_event.on_warning += self.on_module_voltage_warning

    def balance(self) -> None:
        # todo
        pass

    def trigger_safety_disconnect(self) -> None:
        # todo
        pass

    # Event handling for critical events

    def on_critical_battery_system_voltage(self) -> None:
        pass

    def on_critical_battery_system_current(self) -> None:
        pass

    def on_critical_module_temperature(self) -> None:
        # todo
        pass

    def on_critical_chip_temperature(self) -> None:
        # todo
        pass

    def on_critical_module_voltage(self) -> None:
        # todo
        pass

    def on_critical_cell_voltage(self) -> None:
        # todo
        pass

    # Event handling for warning events

    def on_module_temperature_warning(self) -> None:
        pass

    def on_chip_temperature_warning(self) -> None:
        pass

    def on_module_voltage_warning(self) -> None:
        pass

    def on_battery_system_current_warning(self) -> None:
        pass

    def on_battery_system_voltage_warning(self) -> None:
        pass

    def on_cell_voltage_warning(self) -> None:
        pass

    # Event handling for unplausible values
    # Todo: implement loud failing for development time
    # notify user of unplausible state and shut off the system

    def on_implausible_module_temperature(self) -> None:
        # todo
        pass

    def on_implausible_chip_temperature(self) -> None:
        # todo
        pass

    def on_implausible_module_voltage(self) -> None:
        # todo
        pass

    def on_implausible_cell_voltage(self) -> None:
        # todo
        pass

    def on_heartbeat_missed(self, esp_number: int) -> bool:
        print("Heartbeat missed on esp: " + esp_number)
