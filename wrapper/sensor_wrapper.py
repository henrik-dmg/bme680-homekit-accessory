import logging
import random
import time
import bme680
from threading import Thread


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


class WrappedSensor:
    def __init__(self):
        super().__init__()

        # Set the humidity baseline to 40%, an optimal indoor humidity.
        self.hum_baseline = 40.0

        # This sets the balance between humidity and gas reading in the
        # calculation of air_quality_score (25:75, humidity:gas)
        self.hum_weighting = 0.25

        self.gas_baseline = None
        self.did_complete_burnin = False

        try:
            sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        # These oversampling settings can be tweaked to
        # change the balance between accuracy and noise in
        # the data.

        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(600)
        sensor.select_gas_heater_profile(0)

        self.sensor = sensor

    def get_temperature(self) -> float:
        self.sensor.get_sensor_data()
        print("Temperature: {0:.2f} C".format(self.sensor.data.temperature))
        return self.sensor.data.temperature

    def get_humidity(self) -> float:
        self.sensor.get_sensor_data()
        print("Humidity: {0:.2f} %RH".format(self.sensor.data.humidity))
        return self.sensor.data.humidity

    def get_air_quality(self) -> int:
        if (
            self.sensor.get_sensor_data()
            and self.sensor.data.heat_stable
            and self.did_complete_burnin
        ):
            gas = self.sensor.data.gas_resistance
            gas_offset = self.gas_baseline - gas

            hum = self.sensor.data.humidity
            hum_offset = hum - self.hum_baseline

            # Calculate hum_score as the distance from the hum_baseline.
            if hum_offset > 0:
                hum_score = 100 - self.hum_baseline - hum_offset
                hum_score /= 100 - self.hum_baseline
                hum_score *= self.hum_weighting * 100

            else:
                hum_score = self.hum_baseline + hum_offset
                hum_score /= self.hum_baseline
                hum_score *= self.hum_weighting * 100

            # Calculate gas_score as the distance from the gas_baseline.
            if gas_offset > 0:
                gas_score = gas / self.gas_baseline
                gas_score *= 100 - (self.hum_weighting * 100)

            else:
                gas_score = 100 - (self.hum_weighting * 100)

            # Calculate air_quality_score.
            air_quality_score = hum_score + gas_score

            print(
                "Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}".format(
                    gas, hum, air_quality_score
                )
            )
            mapped_aqi_score = air_quality_score / 20
            return random.randint(1, 5)
        else:
            print("Heat stable: {0}, sensor burn in complet: {1}".format(self.sensor.data.heat_stable, self.did_complete_burnin))
            # Return unknown value
            return 0

    def burn_in_sensor_async(self):
        self.burn_in_thread = CustomThread(1, "BurninThread-1", self.burn_in_sensor)
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
                print("Gas: {0} Ohms".format(gas))
                time.sleep(1)

        self.gas_baseline = sum(burn_in_data[-50:]) / 50.0

        print(
            "Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n".format(
                self.gas_baseline, self.hum_baseline
            )
        )

        self.did_complete_burnin = True
