import json

def saveConfiguration(filePath, configuration):
    with open(filePath, "w", encoding = "utf-8") as file:
        json.dump(configuration, file, indent = 4)

def loadConfiguration(filePath):
    with open(filePath, "r", encoding = "utf-8") as file:
        configuration = json.load(file)
    
    validateConfiguration(configuration)

    return configuration

def validateConfiguration(configuration):
    if not isinstance(configuration, dict):
        raise ValueError("Invalid configuration format")

    if configuration.get("version") != 1:
        raise ValueError("Unsupported configuration version")

    if configuration.get("columns") != 3:
        raise ValueError("Invalid dashboard column count")

    widgets = configuration.get("widgets")

    if not isinstance(widgets, list):
        raise ValueError("Invalid widget list")

    widgetIds = set()

    for widget in widgets:
        if not isinstance(widget, dict):
            raise ValueError("Invalid widget configuration")

        widgetType = widget.get("type")
        sensorName = widget.get("sensor")
        widgetId = widget.get("id")

        if widgetType not in ("numeric", "gauge", "graph"):
            raise ValueError("Unsupported widget type")

        if not isinstance(sensorName, str) or not sensorName.strip():
            raise ValueError("Invalid sensor name")

        if widgetId != f"{widgetType}:{sensorName}":
            raise ValueError("Invalid widget ID")

        if widgetId in widgetIds:
            raise ValueError("Duplicate widget ID")

        widgetIds.add(widgetId)

        for key in ("rowSpan", "columnSpan"):
            value = widget.get(key)

            if type(value) is not int or not 1 <= value <= 3:
                raise ValueError(f"Invalid {key}")