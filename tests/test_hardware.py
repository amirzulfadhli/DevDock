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

    def test_ultrasonic_echo_candidates(self):
        echo = next(
            p for p in HC_SR04.pins
            if p.pinId.upper() == "ECHO"
        )

        candidates = findPinsForComponentConnection(
            ESP32_DEVKIT_V1, echo
        )

        self.assertIn(
            34,
            [p.gpioNumber for p in candidates]
        )

    def test_dht22_data_candidates(self):
        data = next(
            p for p in DHT22.pins
            if p.pinId.upper() == "DATA"
        )

        candidates = findPinsForComponentConnection(
            ESP32_DEVKIT_V1, data
        )

        numbers = [p.gpioNumber for p in candidates]

        self.assertIn(21, numbers)
        self.assertNotIn(34, numbers)

    def test_hc_sr04_summary(self):
        summary = summarizeComponentCompatibility(
            ESP32_DEVKIT_V1, HC_SR04
        )

        self.assertEqual(summary["signalConnections"], 2)
        self.assertEqual(summary["matchedConnections"], 2)
        self.assertEqual(len(summary["warnings"]), 1)

if __name__ == "__main__":
    unittest.main()