import time
from events import Events

from measurement_event import MeasurementEvent
from soc_curve import SocCurve


class BatteryCell:
    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = -1000  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 1000  # V
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 3.0  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 4.2  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 3.2  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 4.15  # V
    RELAX_TIME: float = 60.0  # Seconds

    def __init__(self, cell_id: int, module_id: int) -> None:
        # Uninitialized values
        self.voltage: float = 0
        self.balance_pin_state: bool = False
        self.is_initialized: bool = False

        # Initialized values
        self.id = cell_id
        self.module_id = module_id
        self.voltage_event = MeasurementEvent()
        self.communication_event = Events(events=('send_balance_request',))
        self.soc_curve = SocCurve()
        self.last_discharge_time: float = 0

    def soc(self) -> float:
        return self.soc_curve.voltage_to_soc(self.voltage)

    def has_critical_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_CRITICAL or self.voltage > self.UPPER_VOLTAGE_LIMIT_CRITICAL

    def has_warning_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_WARNING or self.voltage > self.UPPER_VOLTAGE_LIMIT_WARNING

    def has_implausible_voltage(self) -> bool:
        return self.voltage < self.LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE \
               or self.voltage > self.UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE

    def update_voltage(self, voltage: float):
        self.voltage = voltage
        if self.has_implausible_voltage():
            self.voltage_event.on_implausible(self)
        elif self.has_critical_voltage():
            self.voltage_event.on_critical(self)
        elif self.has_warning_voltage():
            self.voltage_event.on_warning(self)

    def is_relaxing(self) -> bool:
        now: float = time.time()
        return (now - self.last_discharge_time) < self.RELAX_TIME

    def start_balance_discharge(self, balance_time: float) -> None:
        # Assert that there is a listener reacting to this event
        assert len(self.communication_event.send_balance_request) > 0
        self.communication_event.send_balance_request(self.module_id, self.id, balance_time)
        self.balance_pin_state = True

    def on_balance_discharged_stopped(self) -> None:
        self.balance_pin_state = False
        self.last_discharge_time = time.time()

    def is_balance_discharging(self) -> bool:
        return self.balance_pin_state
