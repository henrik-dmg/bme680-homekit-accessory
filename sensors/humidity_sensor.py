from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class HumiditySensor(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        """Here, we just store a reference to the current temperature characteristic and
        add a method that will be executed every time its value changes.
        """
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, None)

        # Add the services that this Accessory will support with add_preload_service here
        humidity_service = self.add_preload_service("HumiditySensor")
        self.humidity_char = humidity_service.get_characteristic("CurrentRelativeHumidity")

        # Keep reference of sensor
        self.sensor = kwargs.get("sensor")

    @Accessory.run_at_interval(60)
    async def run(self):
        self.humidity_char.set_value(self.sensor.get_humidity())
