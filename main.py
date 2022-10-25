#!/usr/bin/env python3

import logging
import signal
import time

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.air_quality_sensor import AirQualitySensor
from wrapper.sensor_wrapper import WrappedSensor

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")
sensor = WrappedSensor()
sensor.burn_in_sensor()


def make_bridge(accessory_driver):
    bridge = Bridge(accessory_driver, "RaspiBridge")

    bridge.add_accessory(
        TemperatureSensor(accessory_driver, "TemperatureSensor", sensor=sensor)
    )
    bridge.add_accessory(
        HumiditySensor(accessory_driver, "HumiditySensor", sensor=sensor)
    )
    bridge.add_accessory(
        AirQualitySensor(accessory_driver, "AirQualitySensor", sensor=sensor)
    )

    return bridge


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=make_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
