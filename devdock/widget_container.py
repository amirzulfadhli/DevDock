from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QPushButton, QMenu
from PySide6.QtCore import Qt, QMimeData, QEvent
from PySide6.QtGui import QDrag

class DashboardWidget(QFrame):

    def __init__(self, widgetId, title, content, parent = None):
        super().__init__(parent)

        self.widgetId = widgetId
        self.content = content
        self.editMode = True

        self.setStyleSheet("""
            DashboardWidget {
                background-color: #20242b;
                border: 1px solid #414750;
                border-radius: 8px;
            }
        """)

        self.containerLayout = QVBoxLayout(self)
        self.containerLayout.setContentsMargins(6, 6, 6, 6)
        self.containerLayout.setSpacing(6)

        self.header = QFrame()
        self.header.setStyleSheet("""
            QFrame {
                background-color: #303640;
                border-radius: 4px;
            }
            QLabel {
                color: white;
                border: none;
            }
        """)

        self.headerLayout = QHBoxLayout(self.header)

        self.dragHandle = QLabel("::")
        self.dragHandle.setCursor(Qt.CursorShape.OpenHandCursor)
        self.dragHandle.installEventFilter(self)
        self.dragStartPosition = None

        self.titleLabel = QLabel(title)

        self.headerLayout.addWidget(self.dragHandle)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch()

        self.resizeButton = QPushButton("...")
        self.resizeButton.setFixedSize(28, 28)
        self.resizeButton.setToolTip("Resize Widget")

        self.resizeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: non;
                font-size: 20px    
            }
            QPushButton:hover {
                background-color: #414750;
                border-radius: 4px;
            }
        """)

        self.headerLayout.addWidget(self.resizeButton)

        self.resizeButton.clicked.connect(self.showResizeMenu)

        self.containerLayout.addWidget(self.header)
        self.containerLayout.addWidget(self.content, 1)

        self.setAcceptDrops(True)

    def eventFilter(self, watched, event):
        if watched == self.dragHandle:

            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.dragStartPosition = event.position().toPoint()
                    return True
                
            elif event.type() == QEvent.Type.MouseMove:
                if (
                    event.buttons() & Qt.MouseButton.LeftButton
                    and self.dragStartPosition is not None
                ):
                    distance = (
                        event.position().toPoint() - self.dragStartPosition
                    ).manhattanLength()

                    if distance >= QApplication.startDragDistance():
                        self.dragStartPosition = None

                        drag = QDrag(self)

                        mimeData = QMimeData()
                        mimeData.setData("application/x-devdock-widget", self.widgetId.encode("utf-8"))

                        drag.setMimeData(mimeData)
                        drag.setPixmap(self.grab())

                        drag.exec(Qt.DropAction.MoveAction)

                        return True

            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.dragStartPosition = None
        
        return super().eventFilter(watched, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-devdock-widget"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-devdock-widget"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeType = "application/x-devdock-widget"

        if not event.mimeData().hasFormat(mimeType):
            event.ignore()
            return

        sourceId = bytes(
            event.mimeData().data(mimeType)
        ).decode("utf-8")

        targetId = self.widgetId

        workspace = self.parentWidget()

        if workspace and hasattr(workspace, "swapWidgets"):
            if workspace.swapWidgets(sourceId, targetId):
                event.acceptProposedAction()
                return
        
        event.ignore()

    def showResizeMenu(self):
        menu = QMenu(self)

        smallAction = menu.addAction("Small (1 x 1)")
        mediumAction = menu.addAction("Medium (2 x 1)")
        largeAction = menu.addAction("Large (3 x 1)")
        tallAction = menu.addAction("Tall (1 x 2)")
        squareAction = menu.addAction("Square (2 x 2)")

        smallAction.triggered.connect(
            lambda: self.requestResize(1, 1)
        )
        mediumAction.triggered.connect(
            lambda: self.requestResize(1, 2)
        )
        largeAction.triggered.connect(
            lambda: self.requestResize(1, 3)
        )
        tallAction.triggered.connect(
            lambda: self.requestResize(2, 1)
        )
        squareAction.triggered.connect(
            lambda: self.requestResize(2, 2)
        )

        menu.exec(
            self.resizeButton.mapToGlobal(
                self.resizeButton.rect().bottomLeft()
            )
        )

    def requestResize(self, rowSpan, columnSpan):
        workspace = self.parentWidget()

        print("Resize requested:", self.widgetId)
        print("Size:", rowSpan, columnSpan)
        print("Parent:", type(workspace).__name__)
        print("Has resizeWidget:", hasattr(workspace, "resizeWidget"))

        if workspace and hasattr(workspace, "resizeWidget"):
            result = workspace.resizeWidget(
                self.widgetId,
                rowSpan,
                columnSpan
            )

            print("Resize result:", result)

    def setEditMode(self, enabled):
        self.editMode = enabled

        self.dragHandle.setVisible(enabled)
        self.resizeButton.setVisible(enabled)
        self.setAcceptDrops(enabled)