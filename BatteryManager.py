from BatterySystem import BatterySystem
from HeartbeatEvent import HeartbeatEvent
from BatteryModule import BatteryModule

class BatteryManager:
    battery_system = None

    def __init__(self, battery_system: BatterySystem) -> None:
        self.battery_system = battery_system

        for module in self.battery_system.battery_modules:
            module.heartbeat_event.on_heartbeat_missed += self.on_heartbeat_missed

    def balance(self) -> None:
        # todo
        pass

    def trigger_safety_disconnect(self) -> None:
        # todo
        pass

    # Event handling for critical events

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

    def on_heartbeat_missed(self, event: HeartbeatEvent) -> bool:
        print("Heartbeat missed on esp: " + event.esp_number)
