from SocCurve import SocCurve


class BatteryCell:
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 2.8  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 4.2  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 3.2  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 4.15  # V

    def __init__(self, soc_curve: SocCurve):
        # Uninitialized values
        self.voltage: float = 0
        self.balance_pin_state: bool = False
        self.is_initialized: bool = False

        self.soc_curve: SocCurve = soc_curve

    def get_soc(self) -> float:
        return self.soc_curve.voltage_to_soc(self.voltage)

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.LOWER_CRITICAL_VOLTAGE_LIMIT or self.voltage > self.UPPER_VOLTAGE_CRITICAL__LIMIT

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_WARNING_VOLTAGE_LIMIT or self.voltage > self.UPPER_WARNING_VOLTAGE_LIMIT

    def update_voltage(self, voltage: float):
        self.voltage = voltage
        if self.has_critical_voltage():
            self.trigger_critical_voltage_event()
        elif self.has_warning_voltage():
            self.trigger_warning_voltage_event()

    def start_balance_discharge(self):
        # todo
        pass

    def stop_balance_discharge(self):
        # todo
        pass

    def is_balance_discharging(self) -> bool:
        return self.balance_pin_state

    def trigger_implausible_voltage_event(self):
        # todo
        pass

    def trigger_critical_voltage_event(self):
        # todo
        pass

    def trigger_warning_voltage_event(self):
        # todo
        pass
