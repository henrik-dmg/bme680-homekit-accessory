from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import logging

class HumiditySensor(Accessory):

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, None)

        # Add the services that this Accessory will support with add_preload_service here
        humidity_service = self.add_preload_service("HumiditySensor")
        self.humidity_char = humidity_service.get_characteristic("CurrentRelativeHumidity")
        self.humidity_char.setter_callback = self.humidity_changed

        # Keep reference of sensor
        self.sensor = kwargs.get("sensor")

    @Accessory.run_at_interval(60)
    async def run(self):
        self.humidity_char.set_value(self.sensor.get_humidity())

    def humidity_changed(self, value):
        """This will be called every time the value of the CurrentTemperature
        is changed. Use setter_callbacks to react to user actions, e.g. setting the
        lights On could fire some GPIO code to turn on a LED (see pyhap/accessories/LightBulb.py).
        """
        logging.info('Humidity changed to: ', value)
