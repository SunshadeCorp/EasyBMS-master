from BatteryModule import BatteryModule


class BatterySystem:
    LOWER_VOLTAGE_LIMIT: float = 403.2  # V
    UPPER_VOLTAGE_LIMIT: float = 604.8  # V
    CURRENT_LIMIT: float = 30  # A

    def __init__(self, battery_modules: list):
        # Uninitialized values
        self.battery_modules: list = battery_modules
        self.voltage: float = 0
        self.current: float = 0

    def get_soc(self):
        # todo: collect socs for all cells and return the average value
        pass

    def get_power(self):
        # todo
        pass

    def get_highest_cell_temp(self):
        # todo
        pass

    def get_lowest_cell_temp(self):
        # todo
        pass

    def get_highest_cell_voltage(self):
        # todo
        pass

    def get_highest_voltage_cells(self):
        # todo
        pass
