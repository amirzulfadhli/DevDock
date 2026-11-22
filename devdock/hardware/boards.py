from dataclasses import dataclass, field

@dataclass
class PinDefinition:
    pinId: str
    name: str
    gpioNumber: int | None = None
    capabilities: list[str] = field(default_factory = list)
    inputOnly: bool = False
    reserved: bool = False
    notes: str = ""

@dataclass
class BoardDefinition:
    boardId: str
    name: str
    manufacturer: str
    microcontroller: str
    architecture: str
    logicVoltage: float
    features: list[str] = field(default_factory = list)
    pins: list[PinDefinition] = field(default_factory = list)

ESP32_DEVKIT_V1 = BoardDefinition(
    boardId = "esp32_devkit_v1",
    name = "ESP32 DevKit V1",
    manufacturer = "DOIT",
    microcontroller = "ESP32",
    architecture = "Xtensa LX6",
    logicVoltage = 3.3,
    features = [
        "Wi-Fi",
        "Bluetooth",
        "Digital GPIO",
        "ADC",
        "DAC",
        "PWM",
        "I2C",
        "SPI",
        "UART"
    ],
    pins = [
        PinDefinition(
            pinId = "gpio21",
            name = "GPIO 21",
            gpioNumber = 21,
            capabilities = ["digital", "i2c", "pwm"],
            notes = "Default I2c SDA"
        ),
        PinDefinition(
            pinId = "gpio22",
            name = "GPIO 22",
            gpioNumber = 22,
            capabilities = ["digital", "i2c", "pwm"],
            notes = "Default I2C SCL"
        ),
        PinDefinition(
            pinId = "gpio34",
            name = "GPIO 34",
            gpioNumber = 34,
            capabilities = ["digital", "adc"],
            inputOnly = True,
            notes = "No internal pull-up or pull-down"
        ),
        PinDefinition(
            pinId = "gpio18",
            name = "GPIO 18",
            gpioNumber = 18,
            capabilities = ["digital", "spi", "pwm"],
            notes = "Default VSPI clock"
        ),
        PinDefinition(
            pinId = "gpio19",
            name = "GPIO 19",
            gpioNumber = 19,
            capabilities = ["digital", "spi", "pwm"],
            notes = "Default VSPI MISO"
        ),
        PinDefinition(
            pinId = "gpio23",
            name = "GPIO 23",
            gpioNumber = 23,
            capabilities = ["digital", "spi", "pwm"],
            notes = "Default VSPI MOSI"
        ),
        PinDefinition(
            pinId = "gpio25",
            name = "GPIO25",
            gpioNumber = 25,
            capabilities = ["digital", "adc", "dac", "pwm"],
            notes = "ADC2; ADC access conflicts with Wi-Fi"
        ),
        PinDefinition(
            pinId = "gpio26",
            name = "GPIO 26",
            gpioNumber = 26,
            capabilities = ["digital", "adc", "dac", "pwm"],
            notes = "ADC2; ADC access conflicts with Wi-Fi"
        ),
        PinDefinition(
            pinId = "gpio32",
            name = "GPIO 32",
            gpioNumber = 32,
            capabilities = ["digital", "adc", "pwm"],
            notes  = "ADC1"
        ),
        PinDefinition(
            pinId = "gpio33",
            name = "GPIO 33",
            gpioNumber = 33,
            capabilities = ["digital", "adc", "pwm"],
            notes = "ADC1"
        ),
        PinDefinition(
            pinId = "gpio1",
            name = "GPIO 1",
            gpioNumber = 1,
            capabilities = ["digital", "uart"],
            reserved = True,
            notes = "UART0 TX; used for serial communication"
        ),
        PinDefinition(
            pinId = "gpio3",
            name = "GPIO 3",
            gpioNumber = 3,
            capabilities = ["digital", "uart"],
            reserved = True,
            notes = "UART0 RX; used for serial communication"
        ),
        PinDefinition(
            pinId = "3v3",
            name = "3V3",
            capabilities = ["power"],
            notes = "3.3v power supply"
        ),
        PinDefinition(
            pinId = "gnd",
            name = "GND",
            capabilities = ["ground"],
            notes = "Ground reference"
        )
    ]
)

BOARD_REGISTRY: dict[str, BoardDefinition] = {
    ESP32_DEVKIT_V1.boardId: ESP32_DEVKIT_V1
}

def getBoard(boardId: str) -> BoardDefinition | None:
    return BOARD_REGISTRY.get(boardId)

def getAvailableBoards() -> list[BoardDefinition]:
    return list(BOARD_REGISTRY.values())