import time

from battery_cell import BatteryCell
from battery_cell_list import BatteryCellList
from battery_system import BatterySystem
from slave_communicator import SlaveCommunicator


class BatterySystemBalancer:
    MIN_CELL_DIFF_FOR_BALANCING: float = 0.010  # V
    MAX_CELL_DIFF_FOR_BALANCING: float = 0.5  # V
    BALANCE_DISCHARGE_TIME: float = 120.0  # Seconds
    BALANCE_RELAX_TIME: float = 20.0  # Seconds

    def __init__(self, battery_system: BatterySystem, slave_communicator: SlaveCommunicator):
        self.battery_system = battery_system
        self.slave_communicator = slave_communicator

        self.enabled: bool = True
        self.ignore_slaves: set[int] = set()

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

    def balance(self) -> None:
        if not self.enabled:
            return

        possible_cells: BatteryCellList = self.cells()

        if possible_cells.in_relax_time() or possible_cells.currently_balancing():
            print(f'{time.time():.0f} Battery System is balancing. {self.battery_system}', flush=True)
            return

        try:
            highest_voltage = possible_cells.highest_voltage()
        except TypeError:
            print(f'TypeError: some voltages not set! {self.battery_system}')
            return
        lowest_voltage = possible_cells.lowest_voltage()

        cell_diff: float = highest_voltage - lowest_voltage

        print(f'cell_diff: {cell_diff:.3f} V', flush=True)

        if cell_diff < self.MIN_CELL_DIFF_FOR_BALANCING:
            print('Min cell diff was not reached')
            return

        if cell_diff > self.MAX_CELL_DIFF_FOR_BALANCING:
            print('[WARNING] Difference in cell voltages is too high for balancing.'
                  'The system will not perform balancing')
            return

        required_voltage: float = max(lowest_voltage + self.MIN_CELL_DIFF_FOR_BALANCING,
                                      BatteryCell.soc_to_voltage(0.15))
        cells_to_discharge: list[BatteryCell] = possible_cells.voltage_above(required_voltage)

        print('start discharching cells', end='')
        for cell in cells_to_discharge:
            # print(f'{cell.module_id}:{cell.id}({cell.voltage:.3f}V) ', end='')
            cell.start_balance_discharge(self.BALANCE_DISCHARGE_TIME)
        print('.\n')

        # Cells are now discharging until the BMS slave resets the balance pins
