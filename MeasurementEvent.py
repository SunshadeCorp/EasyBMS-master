from events import Events


class MeasurementEvent(Events):
    __events__ = ('on_critical', 'on_warning', 'on_implausible')