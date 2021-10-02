import paho.mqtt.client as mqtt
import sched
import time
import yaml
from pathlib import Path
from typing import Any, Dict

from battery_manager import BatteryManager
from battery_system import BatterySystem
from slave_communicator import SlaveCommunicator, get_config


def balance_task():
    battery_manager.balance()
    scheduler.enter(delay=5, priority=1, action=balance_task)  # delay in seconds


if __name__ == '__main__':
    config = get_config('config.yaml')
    scheduler = sched.scheduler()
    battery_system = BatterySystem(config['number_of_battery_modules'])
    slave_communicator = SlaveCommunicator(config, battery_system, scheduler)
    battery_manager = BatteryManager(battery_system, slave_communicator)

    scheduler.enter(delay=0, priority=1, action=slave_communicator.send_heartbeat)
    scheduler.enter(delay=0, priority=1, action=balance_task)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')
