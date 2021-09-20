from events import Events


class HeartbeatEvent(Events):
    __events__ = ('on_heartbeat', 'on_heartbeat_missed')
    esp_number: int

    def __init__(self, esp_number):
        self.esp_number = esp_number
