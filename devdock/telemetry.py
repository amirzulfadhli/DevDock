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