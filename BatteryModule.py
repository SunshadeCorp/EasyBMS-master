class BatteryModule:
    cells = None
    voltage = None
    module_temp1 = None
    module_temp2 = None
    chip_temp = None
    heartbeat_timestamp = None

    lower_module_temp_limit = None
    upper_module_temp_limit = None
    lower_chip_temp_limit = None
    upper_chip_temp_limit = None
    lower_voltage_limit = None
    upper_voltage_limit = None

    def trigger_missed_heartbeat_event(self):
        # todo

    def trigger_critical_temperature_event(self):
        # todo

    def trigger_implausible_temperature_event(self):
        # todo

    def trigger_critical_module_voltage_event(self):
        # todo

    def trigger_implausible_module_voltage_event(self):
        # todo