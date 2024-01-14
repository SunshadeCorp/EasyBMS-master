import time

from battery_cell import BatteryCell


class BatteryCellList(list[BatteryCell]):
    def in_relax_time(self) -> bool:
        return any(cell.is_relaxing() for cell in self.__iter__())

    def set_relax_time(self, seconds: float):
        for cell in self.__iter__():
            cell.relax_time = seconds

    def currently_balancing(self) -> bool:
        return any(cell.is_balance_discharging() for cell in self.__iter__())

    def highest_voltage(self) -> float:
        return max(cell.voltage for cell in self.__iter__())

    def highest_accurate_voltage(self) -> float:
        return max(cell.accurate_voltage for cell in self.__iter__())

    def lowest_voltage(self) -> float:
        return min(cell.voltage for cell in self.__iter__())

    def lowest_accurate_voltage(self) -> float:
        return min(cell.accurate_voltage for cell in self.__iter__())

    def with_voltage_above(self, value: float) -> list[BatteryCell]:
        return [cell for cell in self.__iter__() if cell.voltage > value]

    def with_accurate_voltage_above(self, value: float) -> list[BatteryCell]:
        return [cell for cell in self.__iter__() if cell.accurate_voltage > value]

    def highest_soc(self) -> float:
        return max(cell.soc() for cell in self.__iter__())

    def lowest_soc(self) -> float:
        return min(cell.soc() for cell in self.__iter__())

    def max_diff(self) -> float:
        return self.highest_voltage() - self.lowest_voltage()

    def has_voltage_older_than(self, seconds: float) -> bool:
        return any(not cell.voltage.initialized() or cell.voltage.age_seconds() > seconds for cell in self.__iter__())

    def with_voltage_older_than(self, seconds: float) -> list[BatteryCell]:
        return [cell for cell in self.__iter__() if not cell.voltage.initialized() or cell.voltage.age_seconds() > seconds]

    def has_accurate_readings_older_than(self, seconds: float) -> bool:
        return any(not cell.voltage.initialized() or cell.accurate_voltage.age_seconds() > seconds for cell in self.__iter__())
