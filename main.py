import paho.mqtt.client as mqtt
import sched
import time
import yaml
from pathlib import Path
from typing import Any, Dict

from battery_manager import BatteryManager
from battery_system import BatterySystem


def get_config(filename: str) -> Dict:
    with open(Path(__file__).parent / filename, 'r') as file:
        try:
            cfg = yaml.safe_load(file)
            return cfg
        except yaml.YAMLError as e:
            print(e)


class EasyBMSMaster:
    def __init__(self, master_config):
        credentials = get_config('credentials.yaml')

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message

        self.mqtt_client.username_pw_set(credentials['username'], credentials['password'])
        self.mqtt_client.will_set('master/core/available', 'offline', retain=True)
        self.mqtt_client.connect(host=master_config['mqtt_server'], port=master_config['mqtt_port'], keepalive=60)

        for battery_module in battery_system.battery_modules:
            for battery_cell in battery_module.cells:
                battery_cell.communication_event.send_balance_request += self.send_balance_request

        self.last_time = {}
        self.lines_to_write = {}
        self.last_log_time = time.time()
        for i in range(12):
            self.last_time[i + 1] = 0
            self.lines_to_write[i + 1] = []

        self.mqtt_client.loop_start()

    def send_heartbeat(self):
        self.mqtt_client.publish(topic='master/uptime', payload=f'{time.time() * 1000:.0f}')
        scheduler.enter(delay=1, priority=1, action=self.send_heartbeat)

    def mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        for i in range(12):
            self.mqtt_client.subscribe(f'esp-module/{i + 1}/uptime')
            for j in range(12):
                self.mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/voltage')
                self.mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/balance')
            self.mqtt_client.subscribe(f'esp-module/{i + 1}/module_voltage')
            self.mqtt_client.subscribe(f'esp-module/{i + 1}/module_temps')
            self.mqtt_client.subscribe(f'esp-module/{i + 1}/chip_temp')
        self.mqtt_client.publish('master/core/available', 'online', retain=True)

    def write_logs(self):
        self.last_log_time = time.time()
        for i in self.lines_to_write:
            with open(f'logs/esp-module{i}.log', 'a+') as file:
                for line in self.lines_to_write[i]:
                    print(line, file=file)
                self.lines_to_write[i].clear()

    @staticmethod
    def topic_extract_number(topic: str) -> (int, str,):
        number = topic[topic.find('/') + 1:]
        sub_topic = number[number.find('/') + 1:]
        number = int(number[:number.find('/')])
        return number, sub_topic

    def send_balance_request(self, module_number: int, cell_number: int, balance_time_s: float):
        self.mqtt_client.publish(topic=f'esp-module/{module_number + 1}/cell/{cell_number + 1}/balance_request',
                                 payload=f'{int(balance_time_s * 1000)}')

    def mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        if time.time() - self.last_log_time >= 60:  # log time diffs
            self.write_logs()

        if msg.topic.startswith('esp-module/'):
            esp_number, topic = self.topic_extract_number(msg.topic)
            if len(msg.payload) > 0:
                payload = msg.payload.decode()
                battery_module = battery_system.battery_modules[esp_number - 1]
                if topic == 'uptime':
                    current_time = int(payload)
                    battery_module.update_esp_uptime(current_time)

                    if self.last_time[esp_number] != 0:  # log time diffs
                        diff = current_time - self.last_time[esp_number] - 1000
                        self.mqtt_client.publish(topic=f'esp-module/{esp_number}/timediff', payload=f'{diff}')
                        self.lines_to_write[esp_number].append(f'{current_time},{diff}')
                    self.last_time[esp_number] = current_time

                elif topic.startswith('cell/'):
                    cell_number, sub_topic = self.topic_extract_number(topic)
                    if sub_topic == 'voltage':
                        battery_module.cells[cell_number - 1].update_voltage(float(payload))
                    elif sub_topic == 'is_balancing':
                        if payload == '1':
                            battery_module.cells[cell_number - 1].balance_pin_state = True
                        else:
                            battery_module.cells[cell_number - 1].on_balance_discharged_stopped()
                elif topic == 'module_voltage':
                    battery_module.update_module_voltage(float(payload))
                elif topic == 'module_temps':
                    module_temps = payload.split(',')
                    battery_module.update_module_temps(module_temps[0], module_temps[1])
                elif topic == 'chip_temp':
                    battery_module.update_chip_temp(float(payload))


def balance_task():
    battery_manager.balance()
    scheduler.enter(delay=5, priority=1, action=battery_manager.balance)  # delay in seconds


if __name__ == '__main__':
    config = get_config('config.yaml')
    battery_system = BatterySystem(config['number_of_battery_modules'])
    battery_manager = BatteryManager(battery_system)

    easy_bms_master = EasyBMSMaster(config)

    scheduler = sched.scheduler()
    scheduler.enter(delay=0, priority=1, action=easy_bms_master.send_heartbeat)
    scheduler.enter(delay=0, priority=1, action=balance_task)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')
