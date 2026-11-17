import sys
import json
import random
import serial
import time
import csv
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox
from PySide6.QtCore import QTimer
from datetime import datetime
from serial.tools import list_ports

from devdock.simulator import generateSampleMessage
from devdock.telemetry import classifyNonJson, parseJson, processMessage
from devdock.serial_manager import openSerialConnection
from devdock.serial_manager import openSerialConnection, readAvailableLines, sendSerialLine, getAvailablePorts

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
resetGraphsButton = QPushButton("Reset Graphs")
pauseGraphsButton = QPushButton("Pause Graphs")
exportCsvButton = QPushButton("Export csv")
clearRecordsButton = QPushButton("Clear csv DATA")

graphsPaused = False

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

    for port in getAvailablePorts():
        portSelector.addItem(port, port)

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

def resetGraphs():
    global sessiontStart
    sessionStart = None

    sampleIndex = 0
    temperatureSamples.clear()
    humiditySamples.clear()
    temperatureHistory.clear()
    humidityHistory.clear()

    temperatureCurve.setData([])
    humidityCurve.setData([])

    temperatureLabel.setText("Temperature: --  °C")
    humidityLabel.setText("Humidity: -- %")

resetGraphsButton.clicked.connect(resetGraphs)

def handleTelemetry(rawData):
    global sampleIndex
    global sessionStart

    timestamp = datetime.now().strftime("%H:%M:%S")

    messageType, parseData = processMessage(rawData)

    if isinstance(parseData, dict):
        if sessionStart is None:
            sessionStart = time.monotonic()

        currentSample = round(time.monotonic() - sessionStart, 2)
        temperature = parseData.get("temperature")

        if isinstance(temperature, (int, float)) and not isinstance(temperature, bool):
            temperatureHistory.append(temperature)
            temperatureSamples.append(currentSample)

            if len(temperatureHistory) > 60:
                temperatureHistory.pop(0)
                temperatureSamples.pop(0)
            
            temperatureLabel.setText(f"Temperature: {temperature:.1f} °C")
        
        if not graphsPaused:
            temperatureCurve.setData(temperatureSamples, temperatureHistory)

            minTemp = min(temperatureHistory) - 2
            maxTemp = max(temperatureHistory) + 2
            temperatureGraph.setYRange(minTemp, maxTemp, padding = 0)

        humidity = parseData.get("humidity")

        if isinstance(humidity, (int, float)) and not isinstance(humidity, bool):
            humidityHistory.append(humidity)
            humiditySamples.append(currentSample)

            if len(humidityHistory) > 60:
                humidityHistory.pop(0)
                humiditySamples.pop(0)

            humidityLabel.setText(f"Humidity: {humidity:.1f} %")

            if not graphsPaused:
                humidityCurve.setData(humiditySamples, humidityHistory)
            
        if any(key in parseData for key in ("temperature", "humidity")):
            telemetryRecords.append({
                "timestamp": timestamp,
                "elapsed": currentSample,
                "temperature": temperature if isinstance(temperature, (int, float)) and not
            isinstance(temperature, bool) else "",
                "humidity": humidity if isinstance(humidity, (int, float)) and not
            isinstance(humidity, bool) else ""
            })
            print(telemetryRecords[-1])
    
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
    handleTelemetry(generateSampleMessage())

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

def exportTelemetryCSV():
    print("Telemetry records:", len(telemetryRecords))
    if not telemetryRecords:
        QMessageBox.warning(
            window,
            "No Data",
            "No telemetry records available"
        )
        return

    filePath, _ = QFileDialog.getSaveFileName(
        window,
        "Export Telemetry",
        "devdock-telemetry.csv",
        "CSV Files (*.csv)"
    )

    if not filePath:
        return
    
    try:
        with open(filePath, "w", newline = "", encoding = "utf-8-sig") as file:
            writer = csv.DictWriter(
                file,
                fieldnames = ["timestamp", "elapsed", "temperature", "humidity"]
            )

            writer.writeheader()
            writer.writerows(telemetryRecords)

        QMessageBox.information(
            window,
            "Export Complete",
            "Telemetry exported successfully"
        )
    
    except OSError as error:
        QMessage.warning(window, "Export Failed", str(error))
    
exportCsvButton.clicked.connect(exportTelemetryCSV)

def clearTelemetryRecords():
    if not telemetryRecords:
        return
    
    confirm = QMessageBox.question(
        window,
        "Clear History",
        "Delete all recorded telemetry data?"
    )

    if confirm == QMessageBox.StandardButton.Yes:
        telemetryRecords.clear()

clearRecordsButton.clicked.connect(clearTelemetryRecords)

def toggleGraphsPause():
    global graphsPaused

    graphsPaused = not graphsPaused

    if graphsPaused:
        pauseGraphsButton.setText("Resume Graphs")
    else:
        pauseGraphsButton.setText("Pause Grphs")

        temperatureCurve.setData(temperatureSamples, temperatureHistory)
        humidityCurve.setData(humiditySamples, humidityHistory)

        if temperatureHistory:
            temperatureGraph.setYRange(
                min(temperatureHistory) - 2,
                max(temperatureHistory) + 2,
                padding = 0
            )

pauseGraphsButton.clicked.connect(toggleGraphsPause)

statusLabel = QLabel("Status: Disconnected")

commandInput = QLineEdit()
commandInput.setPlaceholderText("Enter serial command...")

sendButton = QPushButton("Send")
sendButton.setEnabled(False)

temperatureLabel = QLabel("Temperature: -- °C")
humidityLabel = QLabel("Humidity: -- %")

sampleIndex = 0
sessionStart = None
temperatureSamples = []
humiditySamples = []

graphsPaused = False

temperatureGraph = pg.PlotWidget()
temperatureGraph.setTitle("Temperature Telemetry")
temperatureGraph.setLabel("left", "Temperature", units = "°C")
temperatureGraph.setLabel("bottom", "Elapsed Time", units = "s")
temperatureGraph.showGrid(x = True, y = True)

temperatureHistory = []
temperatureCurve = temperatureGraph.plot()

humidityGraph = pg.PlotWidget()
humidityGraph.setTitle("Humidity Telemetry")
humidityGraph.setLabel("left", "Humidity", units = "%")
humidityGraph.setLabel("bottom", "Elapsed Time", units = "s")
humidityGraph.showGrid(x = True, y = True)
humidityGraph.setYRange(0, 100, padding = 0)

humidityHistory = []
humidityCurve = humidityGraph.plot()

telemetryRecords = []

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
actionLayout.addWidget(resetGraphsButton)
actionLayout.addWidget(pauseGraphsButton)
actionLayout.addWidget(exportCsvButton)
actionLayout.addWidget(clearRecordsButton)
actionLayout.addStretch()

commandLayout = QHBoxLayout()

commandLayout.addWidget(commandInput)
commandLayout.addWidget(sendButton)

layout.addLayout(connectionLayout)
layout.addLayout(actionLayout)
layout.addWidget(statusLabel)
layout.addWidget(statsLabel)
layout.addLayout(commandLayout)
layout.addWidget(serialMonitor, 2)

temperatureLayout = QVBoxLayout()

temperatureLayout.addWidget(temperatureLabel)
temperatureLayout.addWidget(temperatureGraph)

humidityLayout = QVBoxLayout()

humidityLayout.addWidget(humidityLabel)
humidityLayout.addWidget(humidityGraph)

graphLayout = QHBoxLayout()

graphLayout.addWidget(temperatureGraph)
graphLayout.addWidget(humidityGraph)

layout.addLayout(graphLayout, 1)

container.setLayout(layout)
window.setCentralWidget(container)

refreshPorts()

serialConnection = None
readBuffer = bytearray()
serialReadTimer = QTimer()

def disconnectSerial(status = "Status: Disconnected"):
    global serialConnection

    serialReadTimer.stop()

    try:
        if serialConnection is not None:
            serialConnection.close()

    except (serial.SerialException, OSError) as error:
        serialMonitor.append(f"[ERROR] Close Failed: {error}")

    finally:
        serialConnection = None
        readBuffer.clear()

        connectButton.setText("Connect")
        statusLabel.setText(status)

        portSelector.setEnabled(True)
        baudSelector.setEnabled(True)
        refreshButton.setEnabled(True)
        simulationButton.setEnabled(True)
        sendButton.setEnabled(True)

def readSerialData():
    if serialConnection is None:
        return
    
    if not serialConnection.is_open:
        disconnectSerial("Status: Connection Lost")
        return
    
    try:
        messages = readAvailableLines(serialConnection, readBuffer)

    except (serial.SerialException, OSError) as error:
        serialMonitor.append(f"[ERROR] {error}")
        disconnectSerial("Status: Read Error")
        return
    
    for message  in messages:
        handleTelemetry(message)
    
serialReadTimer.timeout.connect(readSerialData)

def toggleConnection():
    global serialConnection

    if serialConnection is not None:
        disconnectSerial()
        return
    
    try:
        serialConnection = openSerialConnection(
           portSelector.currentData(),
           int(baudSelector.currentText())
        )
    
    except (serial.SerialException, OSError, ValueError) as error:
        serialConnection = None
        statusLabel.setText("Status: Connection Failed")
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
        sendSerialLine(serialConnection, command)
        commandInput.clear()

    except (serial.SerialException, OSError) as error:
        serialMonitor.append(f"[ERROR] Send failed: {error}")
        disconnectSerial("Status: Write Error")

sendButton.clicked.connect(sendCommand)
commandInput.returnPressed.connect(sendCommand)
connectButton.clicked.connect(toggleConnection)


print(processMessage('{"temperature": 28.5}'))
print(processMessage("hello"))
print(processMessage('{"temperature": 28.5'))


window.show()
sys.exit(app.exec())