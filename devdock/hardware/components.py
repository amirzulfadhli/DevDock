from dataclasses import dataclass, field

@dataclass
class ComponentPinDefinition:
    pinId: str
    name: str
    function: str
    requiredCapability: str
    direction: str
    notes: str = ""

@dataclass
class ComponentDefinition:
    componentId: str
    name: str
    manufacturer: str
    category: str
    description: str
    operatingVoltage: str
    communicationProtocol: str
    requiredCapabilities: list[str] = field(default_factory = list)
    pins: list[ComponentPinDefinition] = field(
        default_factory = list
    )
    notes: str = ""


DHT22 = ComponentDefinition(
    componentId = "dht22",
    name = "DHT22 Temperature and humidity Sensor",
    manufacturer = "Aosong",
    category = "Sensor",
    description = "Digital temperature and humidity sensor",
    operatingVoltage = "3.3V-5.5V",
    communicationProtocol = "DHT single-wire",
    requiredCapabilities = ["digital"],
    pins = [
        ComponentPinDefinition(
            pinId = "vcc",
            name = "VCC",
            function = "Power supply",
            requiredCapability = "power",
            direction = "power",
            notes = "Use a suitab;e regulated supply"
        ),
        ComponentPinDefinition(
            pinId = "data",
            name = "DATA",
            function = "Temperature and humidity data",
            requiredCapability = "digital",
            direction = "bidirectional",
            notes = "Requires a suitable pull-up resistor"
        ),
        ComponentPinDefinition(
            pinId = "nc",
            name = "NC",
            function = "Not connected",
            requiredCapability = "None",
            direction = "none",
            notes = "Leave unconnected"
        ),
        ComponentPinDefinition(
            pinId = "gnd",
            name = "GND",
            function = "Ground",
            requiredCapability = "ground",
            direction = "ground"
        )
    ],
    notes = "Bare four pin DHT22 sensor"
)

HC_SR04 = ComponentDefinition(
    componentId = "hc_sr04",
    name = "HC-SR04 Ultrasonic Distance Sensor",
    manufacturer = "Generic",
    category = "sensor",
    description = "Measures distance using ultrasonic pulses",
    operatingVoltage = "5V",
    communicationProtocol = "Trigger/Echo",
    requiredCapabilities = ["digital"],
    pins = [
        ComponentPinDefinition(
            pinId = "vcc",
            name = "VCC",
            function = "Power supply",
            requiredCapability = "power",
            direction = "power",
        ),
        ComponentPinDefinition(
            pinId = "trig",
            name = "TRIG",
            function = "Trigger measurement",
            requiredCapability = "digital",
            direction = "input"
        ),
        ComponentPinDefinition(
            pinId = "echo",
            name = "ECHO",
            function = "Echo pulse input",
            requiredCapability = "digital",
            direction = "output",
            notes = "Typically 5V logic, level shifting needed for ESP32"
        ),
        ComponentPinDefinition(
            pinId = "gnd",
            name = "GND",
            function = "ground",
            requiredCapability = "ground",
            direction = "ground"
        )
    ],
    notes = "Use voltage level shifting on ECHO when connecting to a 3.3V ESP32"
)

RED_LED = ComponentDefinition(
    componentId = "red_led",
    name = "5mm Red LED",
    manufacturer = "Generic",
    category = "actuator",
    description = "Basic re light emittng diode",
    operatingVoltage = "Approx. 1.8V-2.2V forward voltage",
    communicationProtocol = "CPIO",
    requiredCapabilities = ["digital"],
    pins = [
        ComponentPinDefinition(
            pinId = "anode",
            name = "Anode (+)",
            function = "Positive LED connection",
            requiredCapability = "digital",
            direction = "input",
            notes = "Conenct to GPI through a current limiting resistor"
        ),
        ComponentPinDefinition(
            pinId = "cathode",
            name = "Cathode (-)",
            function = "Negative LEF connection",
            requiredCapability = "ground",
            direction = "ground",
            notes = "Connect to GND in this circuit"
        )
    ],
    notes = "Requires a current limiting resistor, forward voltage is not the supply voltage"
)

SSD1306_OLED = ComponentDefinition(
    componentId = "ssd1306_oled",
    name = "SSD1306 OLED Display",
    manufacturer = "Generic",
    category = "display",
    description = "128x64 monochrome OLED display",
    operatingVoltage = "Module dependent, verify voltage",
    communicationProtocol = "I2C",
    requiredCapabilities = ["i2c"],
    pins = [
        ComponentPinDefinition(
            pinId = "vcc",
            name = "VCC",
            function = "Power supply",
            requiredCapability = "power",
            direction = "power"
        ),
        ComponentPinDefinition(
            pinId = "gnd",
            name = "GND",
            function = "Ground",
            requiredCapability = "ground",
            direction = "ground"
        ),
        ComponentPinDefinition(
            pinId = "sda",
            name = "SDA",
            function = "I2C data",
            requiredCapability = "i2c",
            direction = "bidirectional"
        ),
        ComponentPinDefinition(
            pinId = "scl",
            name = "SCL",
            function = "I2C clock",
            requiredCapability = "i2c",
            direction = "input"
        )
    ],
    notes = "Verify module voltage and I2C pull up voltage before conencting"
)

COMPONENT_REGISTRY: dict[str, ComponentDefinition] = {
    DHT22.componentId: DHT22,
    HC_SR04.componentId: HC_SR04,
    RED_LED.componentId: RED_LED,
    SSD1306_OLED.componentId: SSD1306_OLED
}

def getComponent(componentId: str) -> ComponentDefinition | None:
    return COMPONENT_REGISTRY.get(componentId)

def getAvailableComponents() -> list[ComponentDefinition]:
    return list(COMPONENT_REGISTRY.values())

def validateComponentDatabase() -> list[str]:
    errors = []

    for componentId, component in COMPONENT_REGISTRY.items():
        if componentId != component.componentId:
            errors.append(
                f"Registry ID mismatch: {componentId}"
            )
        
        if not component.name.strip():
            errors.append(
                f"Missing name: {componentId}"
            )
        
        if not component.pins:
            errors.append(
                f"No pins defined: {componentId}"
            )
        
        pinIds = [pin.pinId for pin in component.pins]

        if len(pinIds) != len(set(pinIds)):
            errors.append(
                f"Duplicate pin IDs: {componentId}"
            )

    return errors