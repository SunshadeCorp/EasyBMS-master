class SocCurve:
    data_points = {
        5.0: 1.2,
        4.136: 1.00,
        4.016: 0.9,
        3.913: 0.8,
        3.825: 0.7,
        3.756: 0.6,
        3.678: 0.5,
        3.641: 0.4,
        3.615: 0.3,
        3.579: 0.2,
        3.499: 0.1,
        3.420: 0.0,
        0: -0.2
    }

    def __init__(self):
        # todo
        pass

    def voltage_to_soc(self, cell_voltage):
        assert 0 < cell_voltage < 5

        self.data_points = dict(sorted(self.data_points.items()))
        lower_voltage = min(self.data_points)
        upper_voltage = max(self.data_points)

        for table_voltage in self.data_points:
            if cell_voltage >= table_voltage:
                lower_voltage = table_voltage
            else:
                upper_voltage = table_voltage
                break

        lower_soc = self.data_points[lower_voltage]
        upper_soc = self.data_points[upper_voltage]

        d = (upper_voltage - cell_voltage) / (upper_voltage - lower_voltage)
        # wenn d = 1 dann cell_voltage = lower_voltage -> nimm lower_soc
        # wenn d = 0 dann cell_voltage = upper_voltage -> nimm upper_soc

        soc = (1 - d) * upper_soc + d * lower_soc

        return soc


if __name__ == '__main__':
    soc_curve = SocCurve()
    print(soc_curve.voltage_to_soc(2))
    print(soc_curve.voltage_to_soc(0.1))
    print(soc_curve.voltage_to_soc(3))
    print(soc_curve.voltage_to_soc(4))
    print(soc_curve.voltage_to_soc(4.9))
