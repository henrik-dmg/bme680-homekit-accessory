from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class TemperatureSensor(Accessory):
    """Implementation of a mock temperature sensor accessory."""

    category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

    def __init__(self, driver, display_name, sensor):
        # If overriding this method, be sure to call the super's implementation first.
        super().__init__(driver, display_name)

        # Add the services that this Accessory will support with add_preload_service here
        temp_service = self.add_preload_service("TemperatureSensor")
        self.temp_char = temp_service.get_characteristic("CurrentTemperature")

        # Keep reference of sensor
        self.sensor = sensor

    @Accessory.run_at_interval(15)
    def run(self):
        self.temp_char.set_value(self.sensor.get_temperature())
