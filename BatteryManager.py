class BatteryManager:
    battery_system = None

    def balance(self):
        # todo

    def trigger_safety_disconnect(self):
        # todo

    # Event handling for critical events

    def on_critical_module_temperature(self):
        # todo

    def on_critical_chip_temperature(self):
        # todo

    def on_critical_module_voltage(self):
        # todo

    def on_critical_cell_voltage(self):
        # todo


    # Event handling for unplausible values
    # Todo: implement loud failing for development time
    # notify user of unplausible state and shut off the system

    def on_implausible_module_temperature(self):
        # todo

    def on_implausible_chip_temperature(self):
        # todo

    def on_implausible_module_voltage(self):
        # todo

    def on_implausible_cell_voltage(self):
        # todo
