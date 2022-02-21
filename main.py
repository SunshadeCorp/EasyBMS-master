import sched

from battery_manager import BatteryManager
from battery_system import BatterySystem
from slave_communicator import SlaveCommunicator
from utils import get_config


def heartbeat_task():
    slave_communicator.send_heartbeat()
    scheduler.enter(delay=1, priority=1, action=heartbeat_task)  # delay in seconds


def balance_task():
    battery_manager.balance()
    scheduler.enter(delay=5, priority=1, action=balance_task)  # delay in seconds


def check_heartbeats_task():
    battery_system.check_heartbeats()
    scheduler.enter(delay=5, priority=1, action=check_heartbeats_task)  # delay in seconds


def info_task():
    slave_communicator.send_battery_system_state()
    scheduler.enter(delay=2, priority=1, action=info_task)  # delay in seconds


if __name__ == '__main__':
    config = get_config('config.yaml')
    scheduler = sched.scheduler()
    battery_system = BatterySystem(config['number_of_battery_modules'], config['number_of_serial_cells'])
    slave_communicator = SlaveCommunicator(config, battery_system)
    battery_manager = BatteryManager(battery_system, slave_communicator)

    scheduler.enter(delay=0, priority=1, action=heartbeat_task)
    scheduler.enter(delay=20, priority=1, action=balance_task)
    scheduler.enter(delay=20, priority=1, action=check_heartbeats_task)
    scheduler.enter(delay=0, priority=1, action=info_task)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')
