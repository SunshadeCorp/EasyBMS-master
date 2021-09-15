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

    def get_soc(self) -> float:
        soc_sum: float = 0

        for module in self.battery_modules:
            soc_sum += module.get_soc()

        return soc_sum / len(self.battery_modules)

    def get_highest_cell_temp(self) -> float:
        # todo
        pass

    def get_lowest_cell_temp(self) -> float:
        # todo
        pass

    def get_highest_cell_voltage(self) -> float:
        # todo
        pass

    def get_highest_voltage_cells(self) -> float:
        # todo
        pass
