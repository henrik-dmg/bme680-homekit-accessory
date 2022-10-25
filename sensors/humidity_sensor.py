from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class HumiditySensor(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, driver, display_name, sensor):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(driver, display_name)

        # Add the services that this Accessory will support with add_preload_service here
        humidity_service = self.add_preload_service("HumiditySensor")
        self.humidity_char = humidity_service.get_characteristic(
            "CurrentRelativeHumidity"
        )

        # Keep reference of sensor
        self.sensor = sensor

    @Accessory.run_at_interval(15)
    def run(self):
        self.humidity_char.set_value(self.sensor.get_humidity())
