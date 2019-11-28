from PyQt5 import QtWidgets, QtCore, QtGui
from configparser import ConfigParser
from datetime import datetime


def readConfig(path, section):
    cfg = ConfigParser()
    cfg.read(path)
    sectionCfg = cfg[section]

    params = dict()
    for key, value in zip(sectionCfg.keys(), sectionCfg.values()):
        if value == "False":
            params[key] = False
        elif value == "True":
            params[key] = True
        elif value == "None":
            params[key] = None
        else:
            params[key] = value
    return params


def getActionLabel(path):
    action = list()
    with open(path, "r") as f:
        action = f.read().split()
    return action


def getCurrentDatetime(datetimeFMT="%Y-%m-%d_%H-%M-%S"):
    """
    Return
    --------
    String: ex."2019-11-7_13-40-34"
    """
    return datetime.now().strftime(datetimeFMT)


def scale_keypoints(height, width, keypoints):
    # Scale each coordinate to 0~1
    temp = keypoints.copy()
    temp[:, :, 0] = temp[:, :, 0] / width
    temp[:, :, 1] = temp[:, :, 1] / height
    return temp[:, :, :2]


class CustomVideoLabel(QtWidgets.QLabel):
    # DEPRECATED
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
            self.resX1,
            self.resY1,
            (self.resX2 - self.resX1),
            (self.resY2 - self.resY1))
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 4, QtCore.Qt.SolidLine))
        painter.drawRect(rect)

    def resetPaint(self):
        self.resX1 = 0
        self.resX2 = 0
        self.resY1 = 0
        self.resY2 = 0
        self.enable = False

    def startPaint(self):
        self.enable = True

    def stopPaint(self):
        self.enable = False

    def getCoord(self):
        return (self.resX1, self.resY1, self.resX2, self.resY2)
