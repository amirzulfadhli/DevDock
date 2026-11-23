from devdock.hardware.boards import PinDefinition, BoardDefinition
from devdock.hardware.components import ComponentDefinition

def pinSupportsCapability(
    pin: PinDefinition,
    capability: str,
) -> bool:
    if pin.reserved:
        return False

    return capability in pin.capabilities

def findCandidatePins(
    board: BoardDefinition,
    capability: str
) -> list[PinDefinition]:
    candidates = []

    for pin in board.pins:
        if pinSupportsCapability(pin, capability):
            candidates.append(pin)

    return candidates

def pinSupportsDirection(
    pin: PinDefinition,
    componentDirection: str
) -> bool:
    if pin.reserved:
        return False

    if componentDirection == "input":
        return not pin.inputOnly

    if componentDirection == "output":
        return True

    if componentDirection == "bidirectional":
        return not pin.inputOnly

    return False

def findPinsForComponentConnection(
    board: BoardDefinition,
    connection: ComponentPinDefinition
) -> list[PinDefinition]:
    candidates = []

    for pin in board.pins:
        if(
            pinSupportsCapability(pin, connection.requiredCapability)
            and pinSupportsDirection(pin, connection.direction)
        ):

            candidates.append(pin)

    return candidates

def getElectricalWarnings(
    board: BoardDefinition,
    component: ComponentDefinition,
    connection: ComponentPinDefinition
) -> list[str]:
    warnings = []

    if (
        board.boardId == "esp32_devkit_v1"
        and component.componentId == "hc_sr04"
        and connection.pinId.upper() == "ECHO"
    ):
        warnings.append(
            "WARNING: HC-SR04 ECHO may output 5V \n"
            "ESP32 GPIO uses 3.3V logic \n"
            "Use appropriate level shifting"
        )
    
    return warnings

def summarizeComponentCompatibility(
    board: BoardDefinition,
    component: ComponentDefinition
) -> dict:
    signalConnections = 0
    matchedConnections = 0
    warnings = []

    for connection in component.pins:
        if connection.requiredCapability in ("power", "ground", "none"):
            continue

        signalConnections +=1

        candidates = findPinsForComponentConnection(
            board, connection
        )

        if candidates:
            matchedConnections +=1

        warnings.extend(
            getElectricalWarnings(board, component, connection)
        )
    
    return {
        "signalConnections": signalConnections,
        "matchedConnections": matchedConnections,
        "warnings": warnings
    }

def recommendComponentPins(
    board: BoardDefinition,
    component: ComponentDefinition
) -> dict[str, str] | None:

    connections = [
        connection
        for connection in component.pins
        if connection.requiredCapability not in (
            "power", "ground", "none"
        )
    ]

    availablePins = set()

    for connection in connections:
        candidates = findPinsForComponentConnection(
            board, connection
        )

        if not candidates:
            return None

        for pin in candidates:
            availablePins.add(pin.pinId)

    if len(availablePins) < len(connections):
        return None

    connections.sort(
        key = lambda connection: len(
            findPinsForComponentConnection(
                board, connection
            )
        )
    )

    assignments = {}
    usedPins = set()

    def assignPin(index: int) -> bool:
        if index == len(connections):
            return True

        connection = connections[index]

        candidates = findPinsForComponentConnection(
            board, connection
        )

        for pin in candidates:
            if pin.pinId in usedPins:
                continue

            assignments[connection.pinId] = pin.name
            usedPins.add(pin.pinId)

            if assignPin(index + 1):
                return True

            usedPins.remove(pin.pinId)
            del assignments[connection.pinId]

        return False
    
    if assignPin(0):
        return assignments
    
    return None