import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

def buildGraph(sensorName):
    graph = pg.PlotWidget()
    graph.setMinimumHeight(200)

    displayName = sensorName.replace("_", " ").title()

    graph.setTitle(f"{displayName} Telemetry")
    graph.setLabel("left", displayName)
    graph.setLabel("bottom","Elapsed Time", units = "s")
    graph.showGrid(x = True, y = True)

    curve = graph.plot()

    return graph, curve

def buildNumericCard(sensorName):
    card = QFrame()
    card.setMinimumHeight(100)

    card.setStyleSheet("""
        QFrame {
            background-color: #20242b;
            border: 1px solid #414750;
            border-radius: 8px;
        }

        QLabel {
            color: white;
            border: none;
        }     
    """)

    cardLayout = QVBoxLayout(card)

    displayName = sensorName.replace("_", " ").title()

    titleLabel = QLabel(displayName)
    titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    valueLabel = QLabel("--")
    valueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    valueLabel.setStyleSheet("font-size: 28px; font-weight: bold")

    cardLayout.addWidget(titleLabel)
    cardLayout.addWidget(valueLabel)

    return card, valueLabel

def buildGauge(sensorName, minimum = 0, maximum = 100):
    card = QFrame()
    card.setMinimumHeight(130)

    card.setStyleSheet("""
        QFrame {
            background-color: #20242b;
            border: 1px solid #414750;
            border-radius: 8px;
        }
        QLabel {
            color: white;
            border: none;
        }
    """)

    cardLayout = QVBoxLayout(card)

    displayName = sensorName.replace("_", " ").title()

    titleLabel = QLabel(displayName)
    titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    valueLabel = QLabel("--")
    valueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    valueLabel.setStyleSheet(
        "font-size: 28px; font weight: bold;"
    )

    gauge = QProgressBar()
    gauge.setRange(minimum, maximum)
    gauge.setValue(minimum)
    gauge.setTextVisible(False)
    gauge.setMinimumHeight(18)

    gauge.setStyleSheet("""
        QProgressBar {
            background-color: #414750;
            border: none;
            border-radius: 8px;
        }
        QProgressBar::chunk {
            background-color: #38bdf8;
            border-radius: 8px;
        }
    """)

    cardLayout.addWidget(titleLabel)
    cardLayout.addWidget(valueLabel)
    cardLayout.addWidget(gauge)

    return card, valueLabel, gauge