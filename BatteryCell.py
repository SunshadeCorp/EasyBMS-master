from BatteryModule import BatteryModule
from SocCurve import SocCurve


class BatteryCell:
    LOWER_VOLTAGE_LIMIT: float = 2.8  # V
    UPPER_VOLTAGE_LIMIT: float = 4.2  # V

    def __init__(self, soc_curve: SocCurve, battery_module: BatteryModule):
        # Uninitialized values
        self.voltage: float = 0
        self.balance_pin_state: bool = False
        self.is_initialized: bool = False

        self.soc_curve: SocCurve = soc_curve
        self.parent_module: BatteryModule = battery_module

    def get_soc(self):
        # todo
        pass

    def start_balance_discharge(self):
        # todo
        pass

    def stop_balance_discharge(self):
        # todo
        pass

    def is_balance_discharging(self):
        #  todo
        pass

    def trigger_implausible_voltage_event(self):
        # todo
        pass

    def trigger_critical_voltage_event(self):
        # todo
        pass
