from PySide6.QtWidgets import QWidget, QGridLayout

class DashboardWorkspace(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.dashboardLayout = QGridLayout(self)
        self.dashboardLayout.setSpacing(10)
        self.dashboardLayout.setContentsMargins(10, 10, 10, 10)

        self.widgets = {}
        self.columns = 3
        self.cellHeight = 200
        self.editMode = True

        for column in range(self.columns):
            self.dashboardLayout.setColumnStretch(column, 1)

    def registerWidget(self, widgetType, sensorName, widget):
        widgetId = f"{widgetType}:{sensorName}"

        if widgetId in self.widgets:
            return False

        self.widgets[widgetId] = {
            "type": widgetType,
            "sensor": sensorName,
            "widget": widget,
            "rowSpan": 1,
            "columnSpan": 1
        }

        self.refreshLayout()

        return True

    def unregisterWidget(self, widgetId):
        if not self.editMode:
            return False

        if widgetId not in self.widgets:
            return False

        widgetInfo = self.widgets.pop(widgetId)
        widget = widgetInfo["widget"]

        self.dashboardLayout.removeWidget(widget)
        widget.hide()
        widget.deleteLater()

        self.refreshLayout()

        return True

    def getWidget(self, widgetId):
        return self.widgets.get(widgetId)

    def refreshLayout(self):
        while self.dashboardLayout.count():
            self.dashboardLayout.takeAt(0)
        
        for r in range(self.dashboardLayout.rowCount()):
            self.dashboardLayout.setRowMinimumHeight(r, 0)

        occupiedCells = set()

        for widgetInfo in self.widgets.values():

            rowSpan = widgetInfo["rowSpan"]
            columnSpan = widgetInfo["columnSpan"]

            row = 0
            column = 0

            while not self.canPlaceWidget(
                occupiedCells,
                row,
                column,
                rowSpan,
                columnSpan
            ):
                column += 1

                if column >= self.columns:
                    column = 0
                    row += 1

            for r in range(row, row + rowSpan):
                self.dashboardLayout.setRowMinimumHeight(r, self.cellHeight)
                
            widgetHeight = (
                rowSpan * self.cellHeight + (rowSpan - 1) * self.dashboardLayout.spacing()
            )

            widgetInfo["widget"].setMinimumHeight(widgetHeight)

            self.dashboardLayout.addWidget(
                widgetInfo["widget"],
                row,
                column,
                rowSpan,
                columnSpan
            )

            print("Grid position:", row, column)
            print("Grid span:", rowSpan, columnSpan)

            for r in range(row, row + rowSpan):
                for c in range(column, column + columnSpan):
                    occupiedCells.add((r,c))

    def swapWidgets(self, sourceId, targetId):
        if sourceId == targetId:
            return False

        if sourceId not in self.widgets:
            return False
        
        if targetId not in self.widgets:
            return False
        
        widgetIds = list(self.widgets.keys())

        sourceIndex = widgetIds.index(sourceId)
        targetIndex = widgetIds.index(targetId)

        widgetIds[sourceIndex], widgetIds[targetIndex] = (
            widgetIds[targetIndex],
            widgetIds[sourceIndex]
        )

        self.widgets = {
            widgetId: self.widgets[widgetId]
            for widgetId in widgetIds
        }
                
        self.refreshLayout()

        return True

        if not self.editMode:
            return False
    
    def resizeWidget(self, widgetId, rowSpan, columnSpan):
        if widgetId not in self.widgets:
            return False

        rowSpan = max(1, min(3, rowSpan))
        columSpan = max(1, min(self.columns, columnSpan))

        self.widgets[widgetId]["rowSpan"] = rowSpan
        self.widgets[widgetId]["columnSpan"] = columnSpan

        self.refreshLayout()

        return True

        if not self.editMode:
            return False

    def canPlaceWidget(self, occupiedCells, row, column, rowSpan, columnSpan):
        if column + columnSpan > self.columns:
            return False
        
        for r in range(row, row + rowSpan):
            for c in range(column, column + columnSpan):
                if (r, c) in occupiedCells:
                    return False
        
        return True

    def setEditMode(self, enabled):
        self.editMode = enabled

        for widgetInfo in self.widgets.values():
            widgetInfo["widget"].setEditMode(enabled)

    def exportConfiguration(self):
        configuration = {
            "version": 1,
            "columns": self.columns,
            "widgets": []
        }

        for widgetId,widgetInfo in self.widgets.items():
            configuration["widgets"].append({
                "id": widgetId,
                "type": widgetInfo["type"],
                "sensor": widgetInfo["sensor"],
                "rowSpan": widgetInfo["rowSpan"],
                "columnSpan": widgetInfo["columnSpan"]
            })
        
        return configuration