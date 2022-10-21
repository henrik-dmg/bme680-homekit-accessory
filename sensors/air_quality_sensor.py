from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class AirQualitySensor(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, None)

        # Add the services that this Accessory will support with add_preload_service here
        aqi_service = self.add_preload_service("AirQualitySensor")
        self.aqi_char = aqi_service.get_characteristic("AirQuality")

        # Keep reference of sensor
        self.sensor = kwargs.get("sensor")

    @Accessory.run_at_interval(60)
    async def run(self):
        # 0 is the value for unknown air quality
        self.aqi_char.set_value(self.sensor.get_air_quality())
