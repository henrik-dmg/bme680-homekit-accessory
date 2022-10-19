from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import random


class AirQualitySensor(Accessory):
    """Implementation of a mock temperature sensor accessory."""

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        """Here, we just store a reference to the current temperature characteristic and
        add a method that will be executed every time its value changes.
        """
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, **kwargs)

        # Add the services that this Accessory will support with add_preload_service here
        aqi_service = self.add_preload_service("AirQualitySensor")
        self.aqi_char = aqi_service.get_characteristic("AirQuality")

    @Accessory.run_at_interval(60)  # Run this method every 60 seconds
    # The `run` method can be `async` as well
    async def run(self):
        """We override this method to implement what the accessory will do when it is
        started.

        We set the current temperature to a random number. The decorator runs this method
        every 60 seconds.
        """
        current_aqi = random.randint(0, 100)
        self.aqi_char.set_value(current_aqi)

    # The `stop` method can be `async` as well
    async def stop(self):
        """We override this method to clean up any resources or perform final actions, as
        this is called by the AccessoryDriver when the Accessory is being stopped.
        """
        print("Stopping accessory.")