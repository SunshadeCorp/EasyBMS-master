import time
from events import Events


from soc_curve import SocCurve
from measurement import Measurement
from measurement import MeasurementEvent
from measurement import MeasurementLimits


class BatteryCell:
    LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 0  # V
    UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE: float = 10  # V
    LOWER_VOLTAGE_LIMIT_CRITICAL: float = 3.0  # V
    UPPER_VOLTAGE_LIMIT_CRITICAL: float = 4.2  # V
    LOWER_VOLTAGE_LIMIT_WARNING: float = 3.2  # V
    UPPER_VOLTAGE_LIMIT_WARNING: float = 4.15  # V

    limits: MeasurementLimits = MeasurementLimits()
    limits.critical_lower = LOWER_VOLTAGE_LIMIT_CRITICAL
    limits.critical_upper = UPPER_VOLTAGE_LIMIT_CRITICAL
    limits.implausible_lower = LOWER_VOLTAGE_LIMIT_IMPLAUSIBLE
    limits.implausible_upper = UPPER_VOLTAGE_LIMIT_IMPLAUSIBLE
    limits.warning_lower = LOWER_VOLTAGE_LIMIT_WARNING
    limits.warning_upper = UPPER_VOLTAGE_LIMIT_WARNING

    DEFAULT_RELAX_TIME: float = 1.0  # Seconds
    INTERNAL_IMPEDANCE: float = 0.000975  # Ohm, for 2P cells

    def __init__(self, cell_id: int, module_id: int) -> None:
        self.voltage: Measurement = Measurement(self, self.limits)
        self.accurate_voltage: Measurement = Measurement(self, self.limits)
        self.balance_pin_state: bool or None = False
        self.id: int = cell_id
        self.module_id: int = module_id
        self.communication_event: Events = Events(events=('send_balance_request',))
        self.soc_curve: SocCurve = SocCurve()
        self.last_discharge_time: float = 0
        self.relax_time = self.DEFAULT_RELAX_TIME

    def __str__(self):
        return f'Module{self.module_id} Cell{self.id}: {self.voltage.value:.2f}V Balance:{self.balance_pin_state}'

    def load_adjusted_voltage(self, current: float):
        return self.voltage.value + (self.INTERNAL_IMPEDANCE * current)

    def load_adjusted_soc(self, current: float) -> float:
        return self.soc_curve.voltage_to_soc(self.load_adjusted_voltage(current))

    def soc(self) -> float:
        return self.soc_curve.voltage_to_soc(self.voltage.value)

    def is_relaxing(self) -> bool:
        now: float = time.time()
        return (now - self.last_discharge_time) < self.relax_time

    def start_balance_discharge(self, balance_time: float) -> None:
        # Assert that there is a listener reacting to this event
        assert len(self.communication_event.send_balance_request) > 0
        self.communication_event.send_balance_request(self.module_id, self.id, balance_time)
        self.balance_pin_state = True

    def on_balance_discharged_stopped(self) -> None:
        if self.balance_pin_state:
            self.balance_pin_state = False
            self.last_discharge_time = time.time()

    def is_balance_discharging(self) -> bool:
        return self.balance_pin_state

    @staticmethod
    def soc_to_voltage(soc: float):
        return SocCurve.soc_to_voltage(soc)
