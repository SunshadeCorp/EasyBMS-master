from typing import Any, Dict

import paho.mqtt.client as mqtt


class EasyBMSMaster:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message

        self.mqtt_client.connect(host="broker.hivemq.com", port=1883, keepalive=60)

        self.mqtt_client.loop_forever()

    def mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        pass

    def mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        pass


if __name__ == '__main__':
    EasyBMSMaster()
