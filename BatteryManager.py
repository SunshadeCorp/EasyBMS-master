from BatterySystem import BatterySystem


class BatteryManager:
    battery_system = None

    def __init__(self, battery_system: BatterySystem) -> None:
        self.battery_system = battery_system

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
