import paho.mqtt.client as mqtt
import time
from typing import Any, Dict

from battery_cell import BatteryCell
from battery_system import BatterySystem
from utils import get_config


class SlaveCommunicator:
    def __init__(self, master_config, battery_system: BatterySystem):
        credentials = get_config('credentials.yaml')

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._mqtt_on_connect
        self._mqtt_client.on_message = self._mqtt_on_message

        self._mqtt_client.username_pw_set(credentials['username'], credentials['password'])
        self._mqtt_client.will_set('master/core/available', 'offline', retain=True)
        self._mqtt_client.connect(host=master_config['mqtt_server'], port=master_config['mqtt_port'], keepalive=60)

        self._battery_system = battery_system
        for battery_module in self._battery_system.battery_modules:
            for battery_cell in battery_module.cells:
                battery_cell.communication_event.send_balance_request += self.send_balance_request

        self._last_time = {}
        # self._lines_to_write = {}
        # self._last_log_time = time.time()
        for i in range(len(self._battery_system.battery_modules)):
            self._last_time[i + 1] = 0
        #     self._lines_to_write[i + 1] = []

        self._mqtt_client.loop_start()

    def send_heartbeat(self):
        self._mqtt_client.publish(topic='master/uptime', payload=f'{time.time() * 1000:.0f}')

    def open_battery_relays(self):
        print('open_battery_relays called')
        import traceback
        print(traceback.format_exc())
        self._mqtt_client.publish(topic='master/relays/battery_plus/set', payload='off')
        self._mqtt_client.publish(topic='master/relays/battery_precharge/set', payload='off')
        self._mqtt_client.publish(topic='master/relays/battery_minus/set', payload='off')
        self._mqtt_client.publish(topic=f'master/can/limits/max_voltage/set', payload='0')
        self._mqtt_client.publish(topic=f'master/can/limits/min_voltage/set', payload='0')
        self._mqtt_client.publish(topic=f'master/can/limits/max_discharge_current/set', payload='0')
        self._mqtt_client.publish(topic=f'master/can/limits/max_charge_current/set', payload='0')

    def close_battery_perform_precharge(self):
        self._mqtt_client.publish(topic='master/relays/perform_precharge', payload='on')

    def send_balance_request(self, module_number: int, cell_number: int, balance_time_s: float):
        self._mqtt_client.publish(topic=f'esp-module/{module_number + 1}/cell/{cell_number + 1}/balance_request',
                                  payload=f'{int(balance_time_s * 1000)}')

    def send_battery_system_state(self):
        for battery_module in self._battery_system.battery_modules:
            min_cell: BatteryCell = battery_module.min_voltage_cell()
            max_cell: BatteryCell = battery_module.max_voltage_cell()
            self._mqtt_client.publish(topic=f'esp-module/{min_cell.module_id + 1}/min_cell_voltage',
                                      payload=f'{min_cell.voltage}')
            self._mqtt_client.publish(topic=f'esp-module/{max_cell.module_id + 1}/max_cell_voltage',
                                      payload=f'{max_cell.voltage}')
        try:
            soc: float = self._battery_system.soc()
            soc *= 100.0
            self._mqtt_client.publish(topic=f'master/can/battery/soc/set', payload=f'{soc:.2f}')
        except AssertionError:
            pass

    @staticmethod
    def _topic_extract_number(topic: str) -> (int, str,):
        number = topic[topic.find('/') + 1:]
        sub_topic = number[number.find('/') + 1:]
        number = int(number[:number.find('/')])
        return number, sub_topic

    # def _write_logs(self):
    #     self._last_log_time = time.time()
    #     for i in self._lines_to_write:
    #         with open(f'logs/esp-module{i}.log', 'a+') as file:
    #             for line in self._lines_to_write[i]:
    #                 print(line, file=file)
    #             self._lines_to_write[i].clear()

    def _mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        for i in range(12):
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/uptime')
            for j in range(12):
                self._mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/voltage')
                self._mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/is_balancing')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/module_voltage')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/module_temps')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/chip_temp')
        self._mqtt_client.publish('master/core/available', 'online', retain=True)

    def _mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        # if time.time() - self._last_log_time >= 60:  # log time diffs
        #     self._write_logs()

        if msg.topic.startswith('esp-module/'):
            esp_number, topic = self._topic_extract_number(msg.topic)
            if len(msg.payload) > 0:
                payload = msg.payload.decode()
                battery_module = self._battery_system.battery_modules[esp_number - 1]
                if topic == 'uptime':
                    current_time = int(payload)
                    battery_module.update_esp_uptime(current_time)

                    if self._last_time[esp_number] != 0:  # log time diffs
                        diff = current_time - self._last_time[esp_number] - 1000
                        self._mqtt_client.publish(topic=f'esp-module/{esp_number}/timediff', payload=f'{diff}')
                    #     self._lines_to_write[esp_number].append(f'{current_time},{diff}')
                    self._last_time[esp_number] = current_time

                elif topic.startswith('cell/'):
                    cell_number, sub_topic = self._topic_extract_number(topic)
                    battery_cell = battery_module.cells[cell_number - 1]
                    if sub_topic == 'voltage':
                        battery_cell.update_voltage(float(payload))
                    elif sub_topic == 'is_balancing':
                        if payload == '1':
                            battery_cell.balance_pin_state = True
                        else:
                            battery_cell.on_balance_discharged_stopped()
                elif topic == 'module_voltage':
                    battery_module.update_module_voltage(float(payload))
                elif topic == 'module_temps':
                    module_temps = payload.split(',')
                    battery_module.update_module_temps(float(module_temps[0]), float(module_temps[1]))
                elif topic == 'chip_temp':
                    battery_module.update_chip_temp(float(payload))
