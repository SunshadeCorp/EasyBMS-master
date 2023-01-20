from battery_cell import BatteryCell


class BatteryCellList(list[BatteryCell]):
    def in_relax_time(self) -> bool:
        for cell in self.__iter__():
            if cell.is_relaxing():
                return True
        return False

    def currently_balancing(self) -> bool:
        for cell in self.__iter__():
            if cell.is_balance_discharging():
                return True
        return False

    def highest_voltage(self) -> float:
        return max(cell.voltage for cell in self.__iter__())

    def lowest_voltage(self) -> float:
        return min(cell.voltage for cell in self.__iter__())

    def voltage_above(self, value: float) -> list[BatteryCell]:
        return [cell for cell in self.__iter__() if cell.voltage > value]

    def max_diff(self) -> float:
        return self.highest_voltage() - self.lowest_voltage()
