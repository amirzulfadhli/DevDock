import json

def parseJson(rawData):
    return json.loads(rawData)

def classifyNonJson(rawData):
    if rawData.lstrip().startswith(("{", "[")):
        return "INVALID JSON"
    
    return "TEXT"

def processMessage(rawData):
    try:
        parsedData = parseJson(rawData)
        return "JSON", parsedData
    
    except json.JSONDecodeError:
        messageType = classifyNonJson(rawData)
        return messageType, None

    return "TEXT"

def extractNumericFields(parsedData):
    if not isinstance(parsedData, dict):
        return {}

    numericFields = {}

    for key, value in parsedData.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numericFields[key] = value

    return numericFields

def updateSensorHistories(histories, numericFields, elapsedTime):
    for sensorName, value in numericFields.items():
        if sensorName not in histories:
            histories[sensorName] = {
                "times": [],
                "values": []
            }

        history = histories[sensorName]
        history["times"].append(elapsedTime)
        history["values"].append(value)

        if len(history["values"]) > 60:
            history["times"].pop(0)
            history["values"].pop(0)