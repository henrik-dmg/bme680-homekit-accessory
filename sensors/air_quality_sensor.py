from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import logging


class AirQualitySensor(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, None)

        # Add the services that this Accessory will support with add_preload_service here
        aqi_service = self.add_preload_service("AirQualitySensor")
        self.aqi_char = aqi_service.get_characteristic("AirQuality")
        self.aqi_char.setter_callback = self.aqi_changed

        # Keep reference of sensor
        self.sensor = kwargs.get("sensor")

    @Accessory.run_at_interval(60)
    async def run(self):
        # 0 is the value for unknown air quality
        self.aqi_char.set_value(self.sensor.get_air_quality())

    def aqi_changed(self, value):
        """This will be called every time the value of the CurrentTemperature
        is changed. Use setter_callbacks to react to user actions, e.g. setting the
        lights On could fire some GPIO code to turn on a LED (see pyhap/accessories/LightBulb.py).
        """
        logging.info('AQI changed to: ', value)
