from events import Events


class SlaveCommunicatorEvents(Events):
    __events__ = ('on_connect', 'on_balancing_enabled_set',)
