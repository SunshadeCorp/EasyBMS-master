import sched
import threading
import time
from typing import Any, Dict

import paho.mqtt.client as mqtt


class EasyBMSMaster:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message

        self.mqtt_client.connect(host='192.168.0.191', port=1883, keepalive=60)

    def loop(self):
        self.mqtt_client.loop_forever()

    def send_heartbeat(self):
        self.mqtt_client.publish(topic='master/uptime', payload=f'{time.time() * 1000:.0f}')
        scheduler.enter(1, 1, self.send_heartbeat)

    def mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        pass

    def mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        pass


if __name__ == '__main__':
    easy_bms_master = EasyBMSMaster()
    mqtt_client_thread = threading.Thread(name='EasyBMSMaster', target=easy_bms_master.loop, daemon=True)
    mqtt_client_thread.start()

    scheduler = sched.scheduler()
    scheduler.enter(1, 1, easy_bms_master.send_heartbeat)
    scheduler.run()
