import time
from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)


class VideoTimer(QtCore.QThread):
    def __init__(self, frequent=20):
        QtCore.QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QtCore.QMutex()

    def run(self):
        with QtCore.QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QtCore.QMutexLocker(self.mutex):
            self.stopped = True

    def isStopped(self):
        with QtCore.QMutexLocker(self.mutex):
            return self.stopped

    def setFPS(self, fps):
        self.frequent = fps

