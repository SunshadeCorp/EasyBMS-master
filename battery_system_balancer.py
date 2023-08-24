import time

from battery_cell import BatteryCell
from battery_cell_list import BatteryCellList
from battery_system import BatterySystem
from slave_communicator import SlaveCommunicator


class BatterySystemBalancer:
    DEFAULT_MIN_CELL_DIFF_FOR_BALANCING: float = 0.003  # V
    DEFAULT_MAX_CELL_DIFF_FOR_BALANCING: float = 0.5  # V
    DEFAULT_BALANCE_DISCHARGE_TIME: float = 120.0  # seconds

    # DEFAULT_BALANCE_RELAX_TIME: float = 20.0  # seconds # unused

    ACCURATE_READINGS_MAX_AGE: float = 20.0  # seconds
    ACCURATE_READINGS_REQUEST_WAIT_TIME: float = 10.0  # seconds
    ACCURATE_READINGS_REQUEST_WAIT_TIME_IDLE: float = 120.0  # seconds

    def __init__(self, battery_system: BatterySystem, slave_communicator: SlaveCommunicator):
        self.battery_system = battery_system
        self.slave_communicator = slave_communicator

        self.enabled: bool = True
        self.ignore_slaves: set[int] = set()
        self.idle: bool = False

        self.min_cell_diff_for_balancing: float = self.DEFAULT_MIN_CELL_DIFF_FOR_BALANCING
        self.max_cell_diff_for_balancing: float = self.DEFAULT_MAX_CELL_DIFF_FOR_BALANCING
        self.balance_discharge_time: float = self.DEFAULT_BALANCE_DISCHARGE_TIME

        self.slave_communicator.events.on_connect += self.publish_config
        self.slave_communicator.events.on_balancing_enabled_set += self.set_enabled
        self.slave_communicator.events.on_balancing_ignore_slaves_set += self.set_ignore_slaves

    def publish_config(self):
        self.slave_communicator.send_balancing_enabled_state(self.enabled)
        self.slave_communicator.send_balancing_ignore_slaves_state(self.ignore_slaves)

    def set_enabled(self, value: str):
        self.enabled = value.lower() == 'true'
        self.slave_communicator.send_balancing_enabled_state(self.enabled)

    def set_ignore_slaves(self, ignore_slaves: set[int]):
        self.ignore_slaves = ignore_slaves
        self.slave_communicator.send_balancing_ignore_slaves_state(self.ignore_slaves)

    def cells(self) -> BatteryCellList:
        return BatteryCellList([cell for module in self.battery_system.battery_modules for cell in module.cells if
                                module.id not in self.ignore_slaves])

    def request_accurate_readings(self):
        if self.idle:
            request_wait_time: float = self.ACCURATE_READINGS_REQUEST_WAIT_TIME_IDLE
        else:
            request_wait_time: float = self.ACCURATE_READINGS_REQUEST_WAIT_TIME
        for module in self.battery_system.battery_modules:
            if module.id in self.ignore_slaves:
                continue
            if time.time() - module.last_accurate_reading_request_time > request_wait_time:
                module.last_accurate_reading_request_time = time.time()
                self.slave_communicator.send_accurate_reading_request(module.id)

    def balance(self) -> None:
        if not self.enabled:
            return

        possible_cells: BatteryCellList = self.cells()

        if possible_cells.in_relax_time() or possible_cells.currently_balancing():
            return

        if possible_cells.accurate_readings_older_than(seconds=self.ACCURATE_READINGS_MAX_AGE):
            self.request_accurate_readings()
            return

        try:
            highest_voltage = possible_cells.highest_accurate_voltage()
        except TypeError:
            print(f'TypeError: some voltages not set! {self.battery_system}')
            return
        lowest_voltage = possible_cells.lowest_accurate_voltage()
        self.slave_communicator.send_balancer_cell_min_max(lowest_voltage, highest_voltage)

        cell_diff: float = highest_voltage - lowest_voltage

        self.slave_communicator.send_balancer_cell_diff(cell_diff)

        self.idle = False

        if cell_diff < self.min_cell_diff_for_balancing:
            # print(f'cell_diff: {cell_diff:.3f} V', 'Min cell diff was not reached', flush=True)
            self.idle = True
            return

        if cell_diff > self.max_cell_diff_for_balancing:
            print(f'cell_diff: {cell_diff:.3f} V', '[WARNING] Difference in cell voltages is too high for balancing.',
                  'The system will not perform balancing', flush=True)
            self.idle = True
            return

        if cell_diff > 0.010:
            possible_cells.set_relax_time(seconds=5.0)
            self.balance_discharge_time = 120.0  # seconds
            min_cell_diff: float = max(self.min_cell_diff_for_balancing, 0.010)
        elif cell_diff > 0.005:
            possible_cells.set_relax_time(seconds=10.0)
            self.balance_discharge_time = 60.0  # seconds
            min_cell_diff: float = max(self.min_cell_diff_for_balancing, 0.005)
        else:
            possible_cells.set_relax_time(seconds=20.0)
            self.balance_discharge_time = 30.0  # seconds
            min_cell_diff: float = max(self.min_cell_diff_for_balancing, 0.003)

        required_voltage: float = max(lowest_voltage + min_cell_diff, BatteryCell.soc_to_voltage(0.15))
        cells_to_discharge: list[BatteryCell] = possible_cells.accurate_voltage_above(required_voltage)

        # print('start discharching cells', end='')
        for cell in cells_to_discharge:
            # print(f'{cell.module_id}:{cell.id}({cell.voltage:.3f}V) ', end='')
            cell.start_balance_discharge(self.balance_discharge_time)
        # print('.\n')

        # Cells are now discharging until the BMS slave resets the balance pins
