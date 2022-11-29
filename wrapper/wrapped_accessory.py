from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR

from wrapper.wrapped_sensor import WrappedSensor


class WrappedAccessory(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, driver, display_name, sensor: WrappedSensor):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(driver, display_name)

        # Add the services that this Accessory will support with add_preload_service here
        humidity_service = self.add_preload_service("HumiditySensor")
        self.humidity_char = humidity_service.get_characteristic(
            "CurrentRelativeHumidity"
        )

        temp_service = self.add_preload_service("TemperatureSensor")
        self.temp_char = temp_service.get_characteristic("CurrentTemperature")

        aqi_service = self.add_preload_service("AirQualitySensor")
        self.aqi_char = aqi_service.get_characteristic("AirQuality")

        # Keep reference of sensor
        self.sensor = sensor

    @Accessory.run_at_interval(15)
    def run(self):
        data = self.sensor.get_data()
        self.humidity_char.set_value(data.humidity)
        self.temp_char.set_value(data.temperature)
        self.aqi_char.set_value(data.aqi_score)
