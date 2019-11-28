import time
from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)


class VideoTimer(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.stopped = False
        self.timeSignal = Communicate()
        self.mutex = QtCore.QMutex()
        self.fps = 0

    def run(self):
        if self.stopped:
            with QtCore.QMutexLocker(self.mutex):
                self.stopped = False
            return
        self.timeSignal.signal.emit("1")

    def stop(self):
        with QtCore.QMutexLocker(self.mutex):
            self.stopped = True

    def setFPS(self, fps):
        self.fps = fps
