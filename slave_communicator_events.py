from events import Events


class SlaveCommunicatorEvents(Events):
    __events__ = ('on_connect', 'on_balancing_enabled_set', 'on_balancing_ignore_slaves_set', 'on_can_limit_recv')
