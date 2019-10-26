from PyQt5 import QtWidgets, uic, QtGui, QtCore
from .video import VideoTimer
from .pose_detect.pose_detect import PoseDetect
import os
import sys
import cv2
import time

current_path = os.getcwd()
qtCreatorFile = current_path + os.sep + "ui" + os.sep + "MainWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
no_video_image_path = "./resource/no_video.jpg"

VIDEO_TYPE_OFFLINE = 0
VIDEO_TYPE_REAL_TIME = 1
STATUS_INIT = 0
STATUS_PLAYING = 1
STATUS_PAUSE = 2

# Import Openpose
try:
    sys.path.append("/home/ppcb/openpose/openpose/build/python")
    from openpose import pyopenpose as op
except ImportError as e:
    print("Error: OpenPose library could not be found.")
    raise e


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        params = dict()
        params["model_folder"] = "/home/ppcb/openpose/openpose/models/"
        # params["process_real_time"] = True
        params["net_resolution"] = "352x240"
        # params["net_resolution"] = "-1x320"
        # params["logging_level"] = 0

        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()

        self.poseDetect = PoseDetect()
        self.videoPath = ""
        self.status = STATUS_INIT
        self.videoType = VIDEO_TYPE_OFFLINE
        self.playCapture = cv2.VideoCapture()
        self.drawRestrict = False

        self.initQt()

    def initQt(self):
        self.chooseFileBtn.clicked.connect(self.chooseFile)
        init_image = QtGui.QPixmap(no_video_image_path).scaled(
            self.videoLabel.width(), self.videoLabel.height()
        )
        self.videoLabel.setPixmap(init_image)

        self.playBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.switchVideo)
        self.setBtn.clicked.connect(self.setRestrict)
        self.resetBtn.clicked.connect(self.resetRestrict)
        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)

        self.videoTimer = VideoTimer()
        self.videoTimer.timeSignal.signal[str].connect(self.showVideoImages)

    def closeEvent(self, event):
        accept = QtWidgets.QPushButton()
        cancel = QtWidgets.QPushButton()
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "關閉", "是否關閉！")
        msg.addButton(accept, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cancel, QtWidgets.QMessageBox.RejectRole)
        accept.setText("確定")
        cancel.setText("取消")
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            event.accept()

    def chooseFile(self):
        last_file_path = self.videoPath
        file_path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose File", current_path
        )

        video_path = last_file_path if file_path[0] == "" else file_path[0]

        self.setVideo(video_path, VIDEO_TYPE_OFFLINE)

    def setTimerFPS(self, bias=0):
        fps = self.playCapture.get(cv2.CAP_PROP_FPS)
        print("Video FPS: ", fps)
        # fps = fps / 2 if fps <
        self.videoTimer.setFPS(fps / 2)

    def setVideo(self, path, videoType):
        self.reset()
        self.videoPath = path
        self.videoType = videoType

    def reset(self):
        self.videoTimer.stop()
        self.playCapture.release()
        self.status = STATUS_INIT
        self.playBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    def resetRestrict(self):
        self.poseDetect.restrict.reset()
        self.x1TextEdit.setText("0")
        self.x2TextEdit.setText("0")
        self.y1TextEdit.setText("0")
        self.y2TextEdit.setText("0")

    def showVideoImages(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]

                startTime = time.time()

                # self.poseDetect.setStartTime(startTime)
                datum = op.Datum()
                datum.cvInputData = frame
                self.opWrapper.emplaceAndPop([datum])

                rest = self.videoLabel.getCoord()
                if sum(rest) != 0:
                    print("SET RESTRICT")
                    self.poseDetect.setRestrict(rest)

                self.poseDetect.setPoseKeypoints(datum.poseKeypoints, frame)
                self.poseDetect.poseStart()
                frame = self.poseDetect.getFrame()

                endTime = time.time()
                print("Process time: ", endTime - startTime)

                self.infoTextBrowser.setText(self.poseDetect.getActionCountText())

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                temp_image = QtGui.QImage(
                    rgb.flatten(), width, height, QtGui.QImage.Format_RGB888
                )
                temp_pixmap = QtGui.QPixmap.fromImage(temp_image)
                self.videoLabel.setPixmap(temp_pixmap)
            else:
                if self.videoType is VIDEO_TYPE_OFFLINE:
                    self.reset()
                    self.playBtn.setIcon(
                        self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop)
                    )
                return
        else:
            self.reset()

    def switchVideo(self):
        if self.videoPath == "":
            self.infoTextBrowser.setText("No Video")
            return

        if self.status is STATUS_INIT:
            self.playCapture.open(self.videoPath)
            self.setTimerFPS()
            self.videoTimer.start()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
            )
        elif self.status is STATUS_PLAYING:
            self.videoTimer.stop()
            if self.videoType is VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
            )
        elif self.status is STATUS_PAUSE:
            if self.videoType is VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.videoPath)
            self.videoTimer.start()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
            )

        self.status = (STATUS_PLAYING, STATUS_PAUSE, STATUS_PLAYING)[self.status]

    def setRestrict(self):
        """ Give Restrict coordinate to pose_detect"""
        try:
            x1 = int(self.x1TextEdit.toPlainText())
        except ValueError:
            x1 = 0
        try:
            x2 = int(self.x2TextEdit.toPlainText())
        except ValueError:
            x2 = 0
        try:
            y1 = int(self.y1TextEdit.toPlainText())
        except ValueError:
            y1 = 0
        try:
            y2 = int(self.y2TextEdit.toPlainText())
        except ValueError:
            y2 = 0

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self.poseDetect.setRestrict(x1, y1, x2, y2)

    def start(self):
        """
        Start draw restrict area
        """
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.videoLabel.setCursor(QtCore.Qt.CrossCursor)
        self.videoLabel.start()

    def stop(self):
        """
        Stop draw restrict area
        """
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.videoLabel.setCursor(QtCore.Qt.ArrowCursor)
        self.videoLabel.stop()

