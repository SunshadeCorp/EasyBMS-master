import sched
import threading
import time
from typing import Any, Dict

import paho.mqtt.client as mqtt

from battery_manager import BatteryManager
from battery_system import BatterySystem


class EasyBMSMaster:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message

        self.mqtt_client.connect(host='192.168.0.191', port=1883, keepalive=60)
        self.last_time = {}
        self.lines_to_write = {}
        self.last_log_time = time.time()
        for i in range(12):
            self.mqtt_client.subscribe(f'esp-module{i + 1}/uptime_slave')
            self.last_time[i + 1] = 0
            self.lines_to_write[i + 1] = []

    def loop(self):
        self.mqtt_client.loop_forever()

    def send_heartbeat(self):
        self.mqtt_client.publish(topic='master/uptime', payload=f'{time.time() * 1000:.0f}')
        scheduler.enter(1, 1, self.send_heartbeat)

    def mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        pass

    def mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        if time.time() - self.last_log_time >= 60:
            self.last_log_time = time.time()
            for i in self.lines_to_write:
                with open(f'logs/esp-module{i}.log', 'a+') as file:
                    for line in self.lines_to_write[i]:
                        print(line, file=file)
                    self.lines_to_write[i].clear()
        if msg.topic.endswith('/uptime_slave'):
            topic = msg.topic[:msg.topic.find('/')]
            index = topic[10:]
            if not index.isnumeric():
                self.lines_to_write[index].append(f'{topic}: {index} is not numeric!')
                print(f'{topic}: {index} is not numeric!')
                return
            index = int(index)
            print(msg.topic, msg.payload)
            if not msg.payload.decode().isnumeric():
                self.lines_to_write[index].append(f'{topic}: {msg.payload} is not numeric!')
                print(f'{topic}: {msg.payload} is not numeric!')
                return
            current_time = int(msg.payload)
            if self.last_time[index] != 0:
                diff = current_time - self.last_time[index] - 1000
                self.mqtt_client.publish(topic=f'{topic}/timediff',
                                         payload=f'{diff}')
                self.lines_to_write[index].append(f'{current_time},{diff}')
            self.last_time[index] = current_time
            # print(msg.payload)


def balance_task():
    battery_manager.balance()

    delay = 5  # seconds
    priority = 1
    scheduler.enter(delay, priority, battery_manager.balance)


if __name__ == '__main__':
    number_of_battery_modules = 12
    battery_system = BatterySystem(number_of_battery_modules)
    battery_manager = BatteryManager(battery_system)

    easy_bms_master = EasyBMSMaster()
    mqtt_client_thread = threading.Thread(name='EasyBMSMaster', target=easy_bms_master.loop, daemon=True)
    mqtt_client_thread.start()

    scheduler = sched.scheduler()
    scheduler.enter(0, 1, easy_bms_master.send_heartbeat)
    scheduler.enter(0, 1, balance_task)
    scheduler.run()
