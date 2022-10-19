#!/usr/bin/env python3

"""An example of how to setup and start an Accessory.
This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import bme680

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
from temperature_sensor import TemperatureSensor
from humidity_sensor import HumiditySensor

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)


def make_bridge(accessory_driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(accessory_driver, 'RaspiBridge')
    temp_sensor = TemperatureSensor(accessory_driver, 'TempSensor')
    humidity_sensor = HumiditySensor(accessory_driver, 'HumiditySensor')
    bridge.add_accessory(temp_sensor)
    bridge.add_accessory(humidity_sensor)

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
