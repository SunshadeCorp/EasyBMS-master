import sched
import time
import paho.mqtt.client as mqtt
from battery_manager import BatteryManager
from battery_system import BatterySystem
from typing import Any, Dict


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
            self.mqtt_client.subscribe(f'esp-module{i + 1}/cell_voltage')  # TODO cell_voltages
            self.mqtt_client.subscribe(f'esp-module{i + 1}/module_voltage')
            self.mqtt_client.subscribe(f'esp-module{i + 1}/module_temps')
            self.mqtt_client.subscribe(f'esp-module{i + 1}/chip_temp')
            self.last_time[i + 1] = 0
            self.lines_to_write[i + 1] = []
        self.mqtt_client.loop_start()

    def send_heartbeat(self):
        self.mqtt_client.publish(topic='master/uptime', payload=f'{time.time() * 1000:.0f}')
        scheduler.enter(delay=1, priority=1, action=self.send_heartbeat)

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
        if msg.topic.startswith('esp-module'):
            esp_module = msg.topic[:msg.topic.find('/')]
            esp_module_index = esp_module[10:]
            if not esp_module_index.isnumeric():
                self.lines_to_write[esp_module_index].append(f'{esp_module}: {esp_module_index} is not numeric!')
                print(f'{esp_module}: {esp_module_index} is not numeric!')
                return
            esp_module_index = int(esp_module_index)
            if len(msg.payload) > 0:
                battery_module = battery_system.battery_modules[esp_module_index - 1]  # TODO esp 0
                if msg.topic.endswith('/uptime_slave'):
                    # print(msg.topic, msg.payload)
                    if not msg.payload.decode().isnumeric():
                        self.lines_to_write[esp_module_index].append(f'{esp_module}: {msg.payload} is not numeric!')
                        print(f'{esp_module}: {msg.payload} is not numeric!')
                        return
                    current_time = int(msg.payload)
                    battery_module.update_esp_uptime(current_time)
                    if self.last_time[esp_module_index] != 0:
                        diff = current_time - self.last_time[esp_module_index] - 1000
                        self.mqtt_client.publish(topic=f'{esp_module}/timediff', payload=f'{diff}')
                        self.lines_to_write[esp_module_index].append(f'{current_time},{diff}')
                    self.last_time[esp_module_index] = current_time
                    # print(msg.payload)
                if msg.topic.endswith('/cell_voltage'):  # TODO cell_voltages
                    cell_voltages = msg.payload.decode().split(',')
                    cell_voltages.pop()
                    for i, cell_voltage in enumerate(cell_voltages):
                        battery_module.cells[i].update_voltage(float(cell_voltage))
                if msg.topic.endswith('/module_voltage'):
                    battery_module.update_module_voltage(float(msg.payload.decode()))
                if msg.topic.endswith('/module_temps'):
                    module_temps = msg.payload.decode().split(',')
                    battery_module.update_module_temps(module_temps[0], module_temps[1])
                if msg.topic.endswith('/chip_temp'):
                    battery_module.update_chip_temp(float(msg.payload.decode()))


def balance_task():
    battery_manager.balance()
    scheduler.enter(delay=5, priority=1, action=battery_manager.balance)  # delay in seconds


if __name__ == '__main__':
    number_of_battery_modules = 12
    battery_system = BatterySystem(number_of_battery_modules)
    battery_manager = BatteryManager(battery_system)

    easy_bms_master = EasyBMSMaster()

    scheduler = sched.scheduler()
    scheduler.enter(delay=0, priority=1, action=easy_bms_master.send_heartbeat)
    scheduler.enter(delay=0, priority=1, action=balance_task)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')
