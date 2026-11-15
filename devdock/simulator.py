import json
import random

def generateSampleMessage():
    data = {
        "temperature": round(random.uniform(25, 35), 1),
        "humidity": random.randint(50, 80),
        "status": "OK"
    }

    return json.dumps(data)