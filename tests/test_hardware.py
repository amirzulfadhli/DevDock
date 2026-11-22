import unittest

from devdock.hardware.boards import ESP32_DEVKIT_V1
from devdock.hardware.components import HC_SR04, DHT22, getAvailableComponents, validateComponentDatabase
from devdock.hardware.compatibility import pinSupportsCapability, pinSupportsDirection, findPinsForComponentConnection, summarizeComponentCompatibility

class TestHardware(unittest.TestCase):

    def test_component_database(self):
        self.assertEqual(validateComponentDatabase(), [])
        self.assertEqual(len(getAvailableComponents()), 4)

    def test_gpio34_input_only(self):
        pin = next(
            p for p in ESP32_DEVKIT_V1.pins
            if p.gpioNumber == 34
        )

        self.assertFalse(pinSupportsDirection(pin, "input"))
        self.assertTrue(pinSupportsDirection(pin, "output"))
        self.assertFalse(pinSupportsDirection(pin, "bidirectional"))

    def test_reserved_pin_excluded(self):
        reserved = next(
            p for p in ESP32_DEVKIT_V1.pins
            if p.reserved
        )

        self.assertFalse(
            pinSupportsCapability(reserved, "digital")
        )
