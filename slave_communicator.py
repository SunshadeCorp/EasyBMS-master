import paho.mqtt.client as mqtt
import time
from typing import Any, Dict

from battery_cell import BatteryCell
from battery_system import BatterySystem
from utils import get_config


class SlaveCommunicator:
    def __init__(self, master_config: dict, battery_system: BatterySystem):
        credentials = get_config('credentials.yaml')
        self._slave_mapping = get_config('slave_mapping.yaml')

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._mqtt_on_connect
        self._mqtt_client.on_message = self._mqtt_on_message

        self._mqtt_client.username_pw_set(credentials['username'], credentials['password'])
        self._mqtt_client.will_set('master/core/available', 'offline', retain=True)
        if master_config.get('mqtt_ssl', False):
            self._mqtt_client.tls_set(credentials['mqtt_cert_path'])
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
        print(f'open_battery_relays called: {self._battery_system}')
        self._mqtt_client.publish(topic='master/relays/battery_plus/set', payload='off')
        self._mqtt_client.publish(topic='master/relays/battery_precharge/set', payload='off')
        self._mqtt_client.publish(topic='master/relays/battery_minus/set', payload='off')
        self._mqtt_client.publish(topic='master/can/limits/max_voltage/set', payload='0')
        self._mqtt_client.publish(topic='master/can/limits/min_voltage/set', payload='0')
        self._mqtt_client.publish(topic='master/can/limits/max_discharge_current/set', payload='0')
        self._mqtt_client.publish(topic='master/can/limits/max_charge_current/set', payload='0')

    def close_battery_perform_precharge(self):
        self._mqtt_client.publish(topic='master/relays/perform_precharge', payload='on')

    def send_balance_request(self, module_number: int, cell_number: int, balance_time_s: float):
        self._mqtt_client.publish(topic=f'esp-module/{module_number + 1}/cell/{cell_number + 1}/balance_request',
                                  payload=f'{int(balance_time_s * 1000)}')

    def send_battery_system_state(self):
        for battery_module in self._battery_system.battery_modules:
            try:
                min_cell: BatteryCell = battery_module.min_voltage_cell()
                max_cell: BatteryCell = battery_module.max_voltage_cell()
                self._mqtt_client.publish(topic=f'esp-module/{min_cell.module_id + 1}/min_cell_voltage',
                                          payload=f'{min_cell.voltage}')
                self._mqtt_client.publish(topic=f'esp-module/{max_cell.module_id + 1}/max_cell_voltage',
                                          payload=f'{max_cell.voltage}')
            except TypeError:
                pass
        try:
            self._mqtt_client.publish(topic='master/can/battery/soc/set',
                                      payload=f'{self._battery_system.sliding_window_soc() * 100.0:.2f}')
            self._mqtt_client.publish(topic='master/core/load_adjusted_soc',
                                      payload=f'{self._battery_system.load_adjusted_soc() * 100.0:.2f}')
            self._mqtt_client.publish(topic='master/core/soc', payload=f'{self._battery_system.soc() * 100.0:.2f}')
        except (AssertionError, TypeError):
            pass
        try:
            calculated_voltage: float = self._battery_system.calculated_voltage()
            self._mqtt_client.publish(topic='master/core/calculated_system_voltage',
                                      payload=f'{calculated_voltage:.2f}')
            current_power = self._battery_system.current * calculated_voltage
            self._mqtt_client.publish(topic='master/core/system_power',
                                      payload=f'{current_power:.2f}')
            self._mqtt_client.publish(topic='master/core/load_adjusted_calculated_voltage',
                                      payload=f'{self._battery_system.load_adjusted_calculated_voltage():.2f}')
            self._mqtt_client.publish(topic='master/core/max_cell_diff',
                                      payload=f'{self._battery_system.max_cell_diff():.3f}')
        except TypeError:
            pass
        try:
            self._mqtt_client.publish(topic='master/can/battery/temp/set',
                                      payload=f'{self._battery_system.temp():.2f}')
            self._mqtt_client.publish(topic='master/can/battery/max_cell_temp/set',
                                      payload=f'{self._battery_system.highest_module_temp():.2f}')
            self._mqtt_client.publish(topic='master/can/battery/min_cell_temp/set',
                                      payload=f'{self._battery_system.lowest_module_temp():.2f}')
        except TypeError:
            pass

    @staticmethod
    def _topic_extract_id(topic: str) -> (str, str,):
        extracted = topic[topic.find('/') + 1:]
        sub_topic = extracted[extracted.find('/') + 1:]
        extracted = extracted[:extracted.find('/')]
        return extracted, sub_topic

    @staticmethod
    def _topic_extract_number(topic: str) -> (int, str,):
        extracted, sub_topic = SlaveCommunicator._topic_extract_id(topic)
        return int(extracted), sub_topic

    # def _write_logs(self):
    #     self._last_log_time = time.time()
    #     for i in self._lines_to_write:
    #         with open(f'logs/esp-module{i}.log', 'a+') as file:
    #             for line in self._lines_to_write[i]:
    #                 print(line, file=file)
    #             self._lines_to_write[i].clear()

    def _mqtt_on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
        for i in range(len(self._battery_system.battery_modules)):
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/uptime')
            for j in range(12):
                self._mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/voltage')
                self._mqtt_client.subscribe(f'esp-module/{i + 1}/cell/{j + 1}/is_balancing')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/module_voltage')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/module_temps')
            self._mqtt_client.subscribe(f'esp-module/{i + 1}/chip_temp')
        self._mqtt_client.subscribe('esp-module/1/total_system_voltage')
        self._mqtt_client.subscribe(f'esp-module/{len(self._battery_system.battery_modules)}/total_system_current')
        for module_id in self._slave_mapping['slaves']:
            self._mqtt_client.subscribe(f'esp-module/{module_id}/uptime')
        self._mqtt_client.publish('master/core/available', 'online', retain=True)

    def _handle_cell_message(self, topic, battery_module, payload):
        cell_number, sub_topic = self._topic_extract_number(topic)
        battery_cell = battery_module.cells[cell_number - 1]
        if sub_topic == 'voltage':
            battery_cell.update_voltage(float(payload))
        elif sub_topic == 'is_balancing':
            if payload == '1':
                battery_cell.balance_pin_state = True
            else:
                battery_cell.on_balance_discharged_stopped()

    def _handle_uptime_message(self, payload, battery_module, esp_number):
        current_time = int(payload)
        battery_module.update_esp_uptime(current_time)

        if self._last_time[esp_number] != 0:  # log time diffs
            diff = current_time - self._last_time[esp_number] - 1000
            self._mqtt_client.publish(topic=f'esp-module/{esp_number}/timediff', payload=f'{diff}')
        self._last_time[esp_number] = current_time

    def _configure_esp_module(self, extracted_id):
        slave: dict = self._slave_mapping['slaves'][extracted_id]
        config = f"{slave['number']},"
        config += f"{slave.get('total_voltage_measurer', False):d},"
        config += f"{slave.get('total_current_measurer', False):d}"
        self._mqtt_client.publish(f'esp-module/{extracted_id}/set_config', config)

    def _handle_esp_module_message(self, extracted_id, topic, payload):  # noqa: C901
        if extracted_id.isdigit():
            esp_number = int(extracted_id)
            battery_module = self._battery_system.battery_modules[esp_number - 1]
            if topic == 'uptime':
                self._handle_uptime_message(payload, battery_module, esp_number)
            elif topic.startswith('cell/'):
                self._handle_cell_message(extracted_id, topic, payload)
            elif topic == 'module_voltage':
                battery_module.update_module_voltage(float(payload))
            elif topic == 'module_temps':
                module_temps = payload.split(',')
                battery_module.update_module_temps(float(module_temps[0]), float(module_temps[1]))
            elif topic == 'chip_temp':
                battery_module.update_chip_temp(float(payload))
            elif topic == 'total_system_voltage':
                self._battery_system.update_voltage(float(payload))
            elif topic == 'total_system_current':
                payload = payload.split(',')
                self._battery_system.update_current(float(payload[1]))
        elif extracted_id in self._slave_mapping['slaves']:
            if topic == 'uptime':
                self._configure_esp_module(extracted_id)

    def _mqtt_on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        if msg.topic.startswith('esp-module/') and len(msg.payload) > 0:
            payload = msg.payload.decode()
            extracted_id, topic = self._topic_extract_id(msg.topic)
            self._handle_esp_module_message(extracted_id, topic, payload)
