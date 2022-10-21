import logging
import random
import time

import adafruit_bme680
import board


class WrappedSensor:
    def __init__(self):
        super().__init__()

        # Set the humidity baseline to 40%, an optimal indoor humidity.
        self.hum_baseline = 40.0

        # This sets the balance between humidity and gas reading in the
        # calculation of air_quality_score (25:75, humidity:gas)
        self.hum_weighting = 0.25

        self.gas_baseline = None

        # Create sensor object, communicating over the board's default I2C bus
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

        # change this to match the location's pressure (hPa) at sea level
        self.bme680.sea_level_pressure = 1013.25

    def get_temperature(self) -> float:
        return self.bme680.temperature

    def get_humidity(self) -> float:
        return self.bme680.humidity

    def get_air_quality(self) -> int:
        gas = self.bme680.gas
        gas_offset = self.gas_baseline - gas

        hum = self.bme680.humidity
        hum_offset = hum - self.hum_baseline

        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = (100 - self.hum_baseline - hum_offset)
            hum_score /= (100 - self.hum_baseline)
            hum_score *= (self.hum_weighting * 100)

        else:
            hum_score = (self.hum_baseline + hum_offset)
            hum_score /= self.hum_baseline
            hum_score *= (self.hum_weighting * 100)

        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = (gas / self.gas_baseline)
            gas_score *= (100 - (self.hum_weighting * 100))

        else:
            gas_score = 100 - (self.hum_weighting * 100)

        # Calculate air_quality_score.
        air_quality_score = hum_score + gas_score

        print('Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}'.format(
            gas,
            hum,
            air_quality_score))

        return random.randint(0, 5)

    def burn_in_sensor(self):
        # start_time and curr_time ensure that the
        # burn_in_time (in seconds) is kept track of.

        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 300

        burn_in_data = []

        try:
            # Collect gas resistance burn-in values, then use the average
            # of the last 50 values to set the upper limit for calculating
            # gas_baseline.
            print('Collecting gas resistance burn-in data for 5 mins\n')
            while curr_time - start_time < burn_in_time:
                curr_time = time.time()
                gas = self.bme680.gas
                burn_in_data.append(gas)
                print('Gas: {0} Ohms'.format(gas))
                time.sleep(1)

            self.gas_baseline = sum(burn_in_data[-50:]) / 50.0

            print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
                self.gas_baseline,
                self.hum_baseline))
        except KeyboardInterrupt:
            logging.info("Skipping burn-in period for AQI measurements. Not recommended though")
            pass
