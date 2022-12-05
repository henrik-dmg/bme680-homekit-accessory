import logging
import time
from threading import Thread
import math
import bme680


class CustomThread(Thread):
    def __init__(self, threadID, name, workLoad):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.workLoad = workLoad

    def run(self):
        print("Starting " + self.name)
        self.workLoad()
        print("Exiting " + self.name)


class SensorData:
    """Structure for storing BME680 sensor data."""

    def __init__(self, temperature, pressure, humidity, aqi_score):
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.aqi_score = aqi_score


class WrappedSensor:
    def __init__(self):
        super().__init__()

        # Set the humidity baseline to 40%, an optimal indoor humidity.
        self.IDEAL_HUMIDITY = 40.0
        self.IDEAL_TEMPERATURE = 21.0

        self.gas_baseline = 547658
        self.did_complete_burnin = True

        try:
            sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        # These oversampling settings can be tweaked to
        # change the balance between accuracy and noise in
        # the data.

        sensor.set_humidity_oversample(bme680.OS_8X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(600)
        sensor.select_gas_heater_profile(0)

        self.sensor = sensor

    def get_data(self) -> SensorData:
        self.sensor.get_sensor_data()
        aqi_score = self.get_air_quality(self.sensor.data)
        return SensorData(
            temperature=self.sensor.data.temperature,
            humidity=self.sensor.data.humidity,
            pressure=self.sensor.data.pressure,
            aqi_score=aqi_score,
        )

    def get_air_quality(self, data) -> int:
        if data.heat_stable and self.did_complete_burnin:
            temperature_boundary = 100.0 if self.IDEAL_TEMPERATURE < data.temperature else -21.0
            humidity_boundary = 100.0 if self.IDEAL_HUMIDITY < data.humidity else 0.0
            gas_boundary = 500000 if self.gas_baseline < data.gas_resistance else 50000

            # Example (36 - 21) / (100 - 21)
            temperature_deviation_from_ideal = (
                data.temperature - self.IDEAL_TEMPERATURE) / (temperature_boundary - self.IDEAL_TEMPERATURE)
            temperature_score = temperature_deviation_from_ideal * 10

            # Example (63 - 40) / (100 - 40)
            humidity_deviation_from_ideal = (
                data.humidity - self.IDEAL_HUMIDITY) / (humidity_boundary - self.IDEAL_HUMIDITY)
            humidity_score = humidity_deviation_from_ideal * 10

            gas_deviation_from_ideal = (
                data.gas_resistance - self.gas_baseline) / (gas_boundary - self.gas_baseline)
            gas_score = gas_deviation_from_ideal * 80

            total_score = min(100.0, temperature_score +
                              humidity_score + gas_score)
            inverted_score = 100 - total_score

            print(
                f"Temperature Score: {temperature_score}, hum score: {humidity_score}, gas score: {gas_score}, total: {total_score}")

            if inverted_score < 20:
                return 1
            elif inverted_score < 40:
                return 2
            elif inverted_score < 60:
                return 3
            elif inverted_score < 80:
                return 4
            else:
                return 5
        else:
            # Return unknown value
            return 0

    def burn_in_sensor_async(self):
        self.burn_in_thread = CustomThread(
            1, "BurninThread-1", self.burn_in_sensor)
        self.burn_in_thread.start()

    def burn_in_sensor(self):
        # start_time and curr_time ensure that the
        # burn_in_time (in seconds) is kept track of.

        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 300

        burn_in_data = []

        # Collect gas resistance burn-in values, then use the average
        # of the last 50 values to set the upper limit for calculating
        # gas_baseline.
        print("Collecting gas resistance burn-in data for 5 mins\n")
        while curr_time - start_time < burn_in_time:
            curr_time = time.time()
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance
                burn_in_data.append(gas)
                print("Gas: {0} Ohms, %RH: {1:.2f}".format(
                    gas, self.sensor.data.humidity))
                time.sleep(5)

        self.gas_baseline = sum(burn_in_data[-50:]) / 50.0

        print(
            "Gas baseline: {0} Ohms".format(
                self.gas_baseline)
        )

        self.did_complete_burnin = True
