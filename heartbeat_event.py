from events import Events


class HeartbeatEvent(Events):
    __events__ = ('on_heartbeat', 'on_heartbeat_missed')

