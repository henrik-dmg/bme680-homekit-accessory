from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import random

class TemperatureSensor(Accessory):
    """Implementation of a mock temperature sensor accessory."""

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, *args, **kwargs):
        """Here, we just store a reference to the current temperature characteristic and
        add a method that will be executed every time its value changes.
        """
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(*args, **kwargs)

        # Add the services that this Accessory will support with add_preload_service here
        temp_service = self.add_preload_service("TemperatureSensor")
        self.temp_char = temp_service.get_characteristic("CurrentTemperature")

        # Having a callback is optional, but you can use it to add functionality.
        self.temp_char.setter_callback = self.temperature_changed

    def temperature_changed(self, value):
        """This will be called every time the value of the CurrentTemperature
        is changed. Use setter_callbacks to react to user actions, e.g. setting the
        lights On could fire some GPIO code to turn on a LED (see pyhap/accessories/LightBulb.py).
        """
        print("Temperature changed to: ", value)

    @Accessory.run_at_interval(60)  # Run this method every 60 seconds
    # The `run` method can be `async` as well
    async def run(self):
        """We override this method to implement what the accessory will do when it is
        started.

        We set the current temperature to a random number. The decorator runs this method
        every 60 seconds.
        """
        current_temp = random.randint(14, 26)
        self.temp_char.set_value(current_temp)

    # The `stop` method can be `async` as well
    async def stop(self):
        """We override this method to clean up any resources or perform final actions, as
        this is called by the AccessoryDriver when the Accessory is being stopped.
        """
        print("Stopping accessory.")