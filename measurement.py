import time

from events import Events


class MeasurementEvent(Events):
    __events__ = ('on_critical', 'on_warning', 'on_implausible')


class MeasurementLimits:
    def __init__(self):
        self.warning_upper: float = None
        self.warning_lower: float = None
        self.critical_upper: float = None
        self.critical_lower: float = None
        self.implausible_upper: float = None
        self.implausible_lower: float = None


class Measurement:
    def __init__(self, limits: MeasurementLimits):
        self.value: float or None = None
        self.timestamp: float or None = None

        self.limits = limits

        self.implausible_counter: int = 0
        self.critical_counter: int = 0
        self.warning_counter: int = 0

        self.event = MeasurementEvent()

    def has_implausible_value(self) -> bool:
        return not (self.implausible_lower <= self.value <= self.implausible_upper)

    def has_critical_value(self) -> bool:
        return not (self.critical_lower <= self.value <= self.critical_upper)

    def has_warning_value(self) -> bool:
        return not (self.warning_lower <= self.value <= self.warning_upper)

    def update(self, value: float):
        self.value = value
        time.time()

        if self.has_implausible_value():
            self.implausible_counter += 1
            self.event.on_implausible(self)
        elif self.has_critical_value():
            self.critical_counter += 1
            self.implausible_counter = 0
            self.event.on_critical(self)
        elif self.has_warning_value():
            self.warning_counter += 1
            self.implausible_counter = 0
            self.critical_counter = 0
            self.event.on_warning(self)
        else:
            self.warning_counter = 0
            self.implausible_counter = 0
            self.critical_counter = 0
