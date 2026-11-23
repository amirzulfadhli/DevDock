import unittest

from devdock.hardware.boards import ESP32_DEVKIT_V1
from devdock.hardware.components import HC_SR04, DHT22, getAvailableComponents, validateComponentDatabase
from devdock.hardware.compatibility import pinSupportsCapability, pinSupportsDirection, findPinsForComponentConnection, summarizeComponentCompatibility, recommendComponentPins

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

    def test_recommended_pins_are_unique(self):
        assignments = recommendComponentPins(
            ESP32_DEVKIT_V1, HC_SR04
        )

        self.assertIsNotNone(assignments)
        self.assertEqual(len(assignments), 2)

        assignedPins = list(assignments.values())

        self.assertEqual(
            len(assignedPins),
            len(set(assignedPins))
        )
    
    def test_recommended_pins_support_connections(self):
        assignments = recommendComponentPins(
            ESP32_DEVKIT_V1, HC_SR04
        )

        self.assertIsNotNone(assignments)

        for connection in HC_SR04.pins:
            if connection.requiredCapability in ("power", "ground", "none"):
                continue

            assignedName = assignments[connection.pinId]

            pin = next(
                p for p in ESP32_DEVKIT_V1.pins
                if p.name == assignedName
            )

            self.assertTrue(
                pinSupportsCapability(
                    pin, connection.requiredCapability
                )
            )

            self.assertTrue(
                pinSupportsDirection(
                    pin, connection.direction
                )
            )

    def test_insufficient_gpio_return_none(self):
        from devdock.hardware.components import (
            ComponentDefinition,
            ComponentPinDefinition
        )

        connections = []

        for i in range(20):
            connections.append(
                ComponentPinDefinition(
                    pinId = f"signal_{i}",
                    name = f"Signal {i}",
                    function = "Test signal",
                    requiredCapability = "digital",
                    direction = "input"
                )
            )

        testComponent = ComponentDefinition(
            componentId = "gpio_stress_test",
            name = "GPIO Stress Test",
            manufacturer = "Test",
            category = "test",
            description = "Requires more GPIOs than available",
            operatingVoltage = "3.3V",
            communicationProtocol = "GPIO",
            requiredCapabilities = ["digital"],
            pins = connections
        )

        assignments = recommendComponentPins(
            ESP32_DEVKIT_V1,
            testComponent
        )

        self.assertIsNone(assignments)

    def test_backtracking_finds_valid_assignment(self):
        from dataclasses import replace
        from devdock.hardware.components import (
            ComponentDefinition,
            ComponentPinDefinition
        )

        limitedBoard = replace(
            ESP32_DEVKIT_V1,
            pins = [
                pin for pin in ESP32_DEVKIT_V1.pins
                if pin.gpioNumber in (21, 34)
            ]
        )

        testComponent = ComponentDefinition(
            componentId = "backtracking_test",
            name = "Backtracking Test",
            manufacturer = "Test",
            category = "test",
            description = "Tests GPIO reassignment",
            operatingVoltage = "3.3V",
            communicationProtocol = "GPIO",
            pins = [
                ComponentPinDefinition(
                    pinId = "flexible",
                    name = "Flexible Signal",
                    function = "Read signal",
                    requiredCapability = "digital",
                    direction = "output"
                ),
                ComponentPinDefinition(
                    pinId = "restricted",
                    name = "Restricted Signal",
                    function = "Send signal",
                    requiredCapability = "digital",
                    direction = "input"
                )
            ]
        )

        assignments = recommendComponentPins(
            limitedBoard, testComponent
        )

        self.assertEqual(
            assignments,
            {
                "flexible": "GPIO 34",
                "restricted": "GPIO 21"
            }
        )

    def test_restricted_connection_gets_priority(self):
        from dataclasses import replace
        from devdock.hardware.components import (
            ComponentDefinition,
            ComponentPinDefinition
        )

        limitedBoard = replace(
            ESP32_DEVKIT_V1,
            pins = [
                pin for pin in ESP32_DEVKIT_V1.pins
                if pin.gpioNumber in (21, 22, 34)
            ]
        )

        testComponent = ComponentDefinition(
            componentId = "priority_test",
            name = "Priotrity Test",
            manufacturer = "Test",
            category = "test",
            description = "Tests restricted connection priority",
            operatingVoltage = "3.3V",
            communicationProtocol = "GPIO",
            pins = [
                ComponentPinDefinition(
                    pinId = "flexible",
                    name = "Flexible Signal",
                    function = "Read signal",
                    requiredCapability = "digital",
                    direction = "output"
                ),
                ComponentPinDefinition(
                    pinId = "restricted",
                    name = "Restricted Signal",
                    function = "Send signal",
                    requiredCapability = "digital",
                    direction = "input"
                )
            ]
        )

        assignments = recommendComponentPins(
            limitedBoard, testComponent
        )

        self.assertIsNotNone(assignments)
        self.assertIn(
            assignments["restricted"],
            ("GPIO 21", "GPIO 22")
        )
        self.assertNotEqual(
            assignments["flexible"],
            assignments["restricted"]
        )

if __name__ == "__main__":

    unittest.main()