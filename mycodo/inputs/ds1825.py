# coding=utf-8
import time

from mycodo.inputs.base_input import AbstractInput

# Measurements
measurements_dict = {
    0: {
        'measurement': 'temperature',
        'unit': 'C'
    }
}

# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'DS1825',
    'input_manufacturer': 'MAXIM',
    'input_name': 'DS1825',
    'measurements_name': 'Temperature',
    'measurements_dict': measurements_dict,

    'options_enabled': [
        'location',
        'resolution',
        'period',
        'pre_output'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'w1thermsensor', 'w1thermsensor')
    ],

    'interfaces': ['1WIRE'],
    'resolution': [
        ('', 'Use Chip Default'),
        (9, '9-bit, 0.5 °C, 93.75 ms'),
        (10, '10-bit, 0.25 °C, 187.5 ms'),
        (11, '11-bit, 0.125 °C, 375 ms'),
        (12, '12-bit, 0.0625 °C, 750 ms')
    ]
}


class InputModule(AbstractInput):
    """ A sensor support class that monitors the DS1825's temperature """

    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        if not testing:
            from w1thermsensor import W1ThermSensor

            self.location = input_dev.location
            self.resolution = input_dev.resolution
            self.sensor = W1ThermSensor(
                W1ThermSensor.THERM_SENSOR_DS1825, self.location)
            if self.resolution:
                self.sensor.set_resolution(self.resolution)

    def get_measurement(self):
        """ Gets the DS1825's temperature in Celsius """
        self.return_dict = measurements_dict.copy()

        temperature = None
        n = 2
        for i in range(n):
            try:
                temperature = self.sensor.get_temperature()
                break
            except Exception as e:
                if i == n:
                    self.logger.exception(
                        "{cls} raised an exception when taking a reading: "
                        "{err}".format(cls=type(self).__name__, err=e))
                time.sleep(1)

        if temperature == 85:
            self.logger.error(
                "Measurement returned 85 C, "
                "indicating an issue communicating with the sensor.")
            return None
        elif temperature is not None and -55 > temperature > 125:
            self.logger.error(
                "Measurement outside the expected range of -55 C to 125 C: "
                "{temp} C".format(temp=temperature))
            return None

        self.value_set(0, temperature)

        return self.return_dict
