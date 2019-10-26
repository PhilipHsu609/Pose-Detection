from PyQt5 import QtWidgets, QtCore, QtGui


class CustomVideoLabel(QtWidgets.QLabel):
    resX1 = 0
    resY1 = 0
    resX2 = 0
    resY2 = 0
    pressFlag = False
    enable = False

    def mousePressEvent(self, event):
        if self.enable:
            self.pressFlag = True
            self.resX1 = event.x()
            self.resY1 = event.y()

    def mouseReleaseEvent(self, event):
        self.pressFlag = False

    def mouseMoveEvent(self, event):
        if self.pressFlag and self.enable:
            self.resX2 = event.x()
            self.resY2 = event.y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        rect = QtCore.QRect(
            self.resX1, self.resY1, self.resX2 - self.resX1, self.resY2 - self.resY1
        )
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 4, QtCore.Qt.SolidLine))
        painter.drawRect(rect)

    def start(self):
        self.enable = True

    def stop(self):
        self.enable = False

    def getCoord(self):
        return (self.resX1, self.resY1, self.resX2, self.resY2)
