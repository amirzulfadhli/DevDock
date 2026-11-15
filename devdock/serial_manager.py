import serial
from serial.tools import list_ports

def openSerialConnection(port, baudRate):
    return serial.serial_for_url(
        port,
        baudrate = baudRate,
        timeout = 0
    )

def readAvailableLines(connection, buffer):
    incoming = connection.read(connection.in_waiting)
    buffer.extend(incoming)

    messages = []

    while b"\n" in buffer:
        line, _, remaining = buffer.partition(b"\n")
        buffer[:] = remaining
        message = line.decode("utf-8", errors = "replace").strip()

        if message:
            messages.append(message)
    
    return messages

def sendSerialLine(connection, message):
    encodedMessage = (message + "\n").encode("utf-8")
    return connection.write(encodedMessage)

def getAvailablePorts():
    ports = list_ports.comports()
    return [port.device for port in ports]