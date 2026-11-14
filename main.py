import sys
import json
import random
import serial
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox
from PySide6.QtCore import QTimer
from datetime import datetime
from serial.tools import list_ports

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("DevDock")
window.resize(900, 600)

portSelector = QComboBox()
portSelector.addItems({"Select Port"})

connectButton = QPushButton("Connect")
connectButton.setEnabled(False)

clearButton = QPushButton("Clear Monitor")
refreshButton = QPushButton("Refresh Ports")
simulationButton = QPushButton("Start Simulation")
exportButton = QPushButton("Export Logs")
resetStatsButton = QPushButton("Reset Statistics")

baudSelector = QComboBox()
baudSelector.addItems(["9600", "19200", "38400", "57600", "115200"])
baudSelector.setCurrentText("115200")

availablePorts = list_ports.comports()

container = QWidget()
layout = QVBoxLayout()

def exportLogs():
    logText = serialMonitor.toPlainText()

    if not logText.strip():
        return
    
    filePath, _ = QFileDialog.getSaveFileName(
        window, "Export Serial Logs", "devdock-logs.txt", "Text File (*.txt)"
    )

    if not filePath:
        return
    
    try:
        with open(filePath, "w", encoding = "utf-8") as file:
            file.write(logText)

        QMessageBox.information(
            window, "Export Complete", "Serial logs saved succesfully."
        )

    except OSError as error:
        QMessageBox.warning(
            window, "Export Failed", str(error)
        )

exportButton.clicked.connect(exportLogs)

def refreshPorts():
    portSelector.clear()
    portSelector.addItem("Select Port")
    portSelector.addItem("Virtual Loppback (Test)", "loop://")

    for port in list_ports.comports():
        portSelector.addItem(port.device, port.device)

refreshButton.clicked.connect(refreshPorts)

def updateConnectButton():
    connectButton.setEnabled(portSelector.currentData() is not None)
    selectedPort = portSelector.currentText()

    if selectedPort == "Select Port":
        connectButton.setEnabled(False)
    else:
        connectButton.setEnabled(True)

portSelector.currentTextChanged.connect(updateConnectButton)

serialMonitor = QTextEdit()
serialMonitor.document().setMaximumBlockCount(1000)
serialMonitor.setReadOnly(True)
serialMonitor.setPlaceholderText("Waiting for serial data...")

clearButton.clicked.connect(serialMonitor.clear)

messageCounts = {
    "total": 0,
    "JSON": 0,
    "TEXT": 0,
    "INVALID JSON": 0
}

statsLabel = QLabel("Total: 0 | JSON: 0 | Text: 0 | Invalid: 0")

def resetStatistics():
    for key in messageCounts:
        messageCounts[key] = 0

    statsLabel.setText(
        "Total: 0 | JSON: 0 | Text: 0 | Invalid: 0"
    )

resetStatsButton.clicked.connect(resetStatistics)

def handleTelemetry(rawData):
    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        json.loads(rawData)
        messageType = "JSON"

    except json.JSONDecodeError:
        if rawData.lstrip().startswith(("{","}")):
            messageType = "INVALID JSON"
        else:
            messageType = "TEXT"
    
    messageCounts["total"] += 1
    messageCounts[messageType] += 1

    statsLabel.setText(
        f"Total: {messageCounts['total']} |"
        f"JSON: {messageCounts['JSON']} |"
        f"Text: {messageCounts['TEXT']} |"
        f"Invalid: {messageCounts['INVALID JSON']}"
    )

    scrollBar = serialMonitor.verticalScrollBar()
    atBottom = scrollBar.value() >= scrollBar.maximum() - 2

    serialMonitor.append(f"[{timestamp}] [{messageType}] {rawData}")

    if atBottom:
        scrollBar.setValue(scrollBar.maximum())

def generateTelemetry():
    data = {
        "temperature": round(random.uniform(25, 35), 1),
        "humidity": random.randint(50, 80),
        "status": "OK"
    }

    handleTelemetry(json.dumps(data))

telemetryTimer = QTimer()
telemetryTimer.timeout.connect(generateTelemetry)

def toggleSimulation():
    if telemetryTimer.isActive():
        telemetryTimer.stop()
        simulationButton.setText("Start Simulation")
        statusLabel.setText("Status: Disconnected")
    else:
        telemetryTimer.start(1000)
        simulationButton.setText("Stop Simulation")
        statusLabel.setText("Status: Simulation Active")

simulationButton.clicked.connect(toggleSimulation)

statusLabel = QLabel("Status: Disconnected")

commandInput = QLineEdit()
commandInput.setPlaceholderText("Enter serial command...")

sendButton = QPushButton("Send")
sendButton.setEnabled(False)

connectionLayout = QHBoxLayout()

connectionLayout.addWidget(QLabel("Port:"))
connectionLayout.addWidget(portSelector)
connectionLayout.addWidget(QLabel("Baud:"))
connectionLayout.addWidget(baudSelector)
connectionLayout.addWidget(refreshButton)
connectionLayout.addWidget(connectButton)

actionLayout = QHBoxLayout()

actionLayout.addWidget(simulationButton)
actionLayout.addWidget(clearButton)
actionLayout.addWidget(exportButton)
actionLayout.addWidget(resetStatsButton)
actionLayout.addStretch()

commandLayout = QHBoxLayout()

commandLayout.addWidget(commandInput)
commandLayout.addWidget(sendButton)

layout.addLayout(connectionLayout)
layout.addLayout(actionLayout)
layout.addWidget(statusLabel)
layout.addWidget(statsLabel)
layout.addLayout(commandLayout)
layout.addWidget(serialMonitor, 1)

container.setLayout(layout)
window.setCentralWidget(container)

refreshPorts()

serialConnection = None
readBuffer = bytearray()
serialReadTimer = QTimer()

def readSerialData():
    if serialConnection is None or not serialConnection.is_open:
        return
    
    try:
        incoming = serialConnection.read(serialConnection.in_waiting)
        readBuffer.extend(incoming)

        while b"\n" in readBuffer:
            line, _, remaining = readBuffer.partition(b"\n")
            readBuffer[:] = remaining

            message = line.decode("utf-8", errors = "replace").strip()

            if message:
                handleTelemetry(message)

    except (serial.SerialException, OSError) as error:
        serialReadTimer.stop()
        statusLabel.setText("Status: Read Error")
        serialMonitor.append(f"[ERROR] {error}")
    
serialReadTimer.timeout.connect(readSerialData)

def toggleConnection():
    global serialConnection

    if serialConnection is not None and serialConnection.is_open:
        serialReadTimer.stop()
        serialConnection.close()
        serialConnection = None
        readBuffer.clear()

        connectButton.setText("Connect")
        statusLabel.setText("Status: Disconnected")
        portSelector.setEnabled(True)
        baudSelector.setEnabled(True)
        refreshButton.setEnabled(True)
        simulationButton.setEnabled(True)
        sendButton.setEnabled(False)
        return
    
    try:
        serialConnection = serial.serial_for_url(
            portSelector.currentData(),
            baudrate = int(baudSelector.currentText()),
            timeout = 0
        )
    
    except (Serial.SerialException, OSError, ValueError) as error:
        serialConnection = None
        status.Label.setText("Status: Connection Failed")
        serialMonitor.append(f"[ERROR] {error}")
        return
    
    if telemetryTimer.isActive():
        telemetryTimer.stop()
        simulationButton.setText("Start simulation")

    serialReadTimer.start(50)
    readBuffer.clear()

    connectButton.setText("Disconnect")
    statusLabel.setText(f"Status: Connected to {portSelector.currentText()}")
    portSelector.setEnabled(False)
    baudSelector.setEnabled(False)
    refreshButton.setEnabled(False)
    simulationButton.setEnabled(False)
    sendButton.setEnabled(True)

    if portSelector.currentData() == "loop://":
        testData = '{"temperature": 28.5, "humidity": 65, "status": "OK"}\n'
        serialConnection.write(testData.encode("utf-8"))

def sendCommand():
    if serialConnection is None or not serialConnection.is_open:
        return
    
    command = commandInput.text()

    if not command:
        return

    try:
        serialConnection.write((command + "\n").encode("utf-8"))
        commandInput.clear()

    except (serial.SerialException, OSError) as error:
        serialMonitor.append(f"[ERROR] Send failed: {error}")

sendButton.clicked.connect(sendCommand)
commandInput.returnPressed.connect(sendCommand)
connectButton.clicked.connect(toggleConnection)

window.show()
sys.exit(app.exec())