import time

from events import Events


class MeasurementEvent(Events):
    __events__ = ('on_critical', 'on_warning', 'on_implausible')


class MeasurementLimits:
    def __init__(self):
        self.warning_upper: float or None = None
        self.warning_lower: float or None = None
        self.critical_upper: float or None = None
        self.critical_lower: float or None = None
        self.implausible_upper: float or None = None
        self.implausible_lower: float or None = None

class Measurement:
    def __init__(self, limits: MeasurementLimits, owner):
        self.value: float or None = None
        self.timestamp: float or None = None
        self.owner = owner
        self.limits = limits

        self.implausible_counter: int = 0
        self.critical_counter: int = 0
        self.warning_counter: int = 0

        self.event = MeasurementEvent()

    def has_implausible_value(self) -> bool:
        return not (self.limits.implausible_lower <= self.value <= self.limits.implausible_upper)

    def has_critical_value(self) -> bool:
        return not (self.limits.critical_lower <= self.value <= self.limits.critical_upper)

    def has_warning_value(self) -> bool:
        return not (self.limits.warning_lower <= self.value <= self.limits.warning_upper)

    def update(self, value: float):
        self.value = value
        time.time()

        if self.has_implausible_value():
            self.implausible_counter += 1
            self.event.on_implausible(self.owner)
        elif self.has_critical_value():
            self.critical_counter += 1
            self.implausible_counter = 0
            self.event.on_critical(self.owner)
        elif self.has_warning_value():
            self.warning_counter += 1
            self.implausible_counter = 0
            self.critical_counter = 0
            self.event.on_warning(self.owner)
        else:
            self.warning_counter = 0
            self.implausible_counter = 0
            self.critical_counter = 0
