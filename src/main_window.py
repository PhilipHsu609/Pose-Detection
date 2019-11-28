from PyQt5 import QtWidgets, uic, QtGui, QtCore
from .video import VideoTimer
from .pose_detect.pose_detect import PoseDetect
from .pose_detect.track import resetTracker
from .utils import readConfig, getCurrentDatetime
from .logger import Logger, getLogStream
from configparser import ConfigParser
import os
import sys
import cv2
import time

# Import Openpose
try:
    sys.path.append("./openpose/build/python")
    from openpose import pyopenpose as op
except ImportError as e:
    print("Error: OpenPose library could not be found.")
    raise e

logger = Logger("main")

# Load Qt UI
current_path = os.getcwd()
qtCreatorFile = current_path + os.sep + "ui" + os.sep + "MainWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
no_video_image_path = "./resource/no_video.jpg"
save_frame_path = "./frame"

# Variables for OpenCV painter
drawing = False
ix = -1
iy = -1

# Constant for video player
VIDEO_TYPE_OFFLINE = 0
STATUS_INIT = 0
STATUS_PLAYING = 1
STATUS_PAUSE = 2

framePeroid = -1


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Read Openpose Config
        params = readConfig("./config.cfg", "Openpose")

        # Init Openpose
        logger.info("Initialize Openpose")
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()

        self.poseDetect = PoseDetect()
        self.videoPath = ""
        self.status = STATUS_INIT
        self.videoType = VIDEO_TYPE_OFFLINE
        self.playCapture = cv2.VideoCapture()
        self.save = False
        self.saveFrameCount = 0
        self.datetime = None

        self.initQt()

    def initQt(self):
        logger.info("Initialize Qt UI")
        self.chooseFileBtn.clicked.connect(self.chooseFile)
        self.videoLabel.resize(self.videoWidget.size())
        init_image = QtGui.QPixmap(no_video_image_path).scaled(
            self.videoLabel.width(), self.videoLabel.height()
        )
        self.videoLabel.setPixmap(init_image)

        self.playBtn.setIcon(
            self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.switchVideo)
        self.startBtn.clicked.connect(self.startPaint)
        self.resetVideoBtn.clicked.connect(self.resetVideo)
        self.resetRestrictBtn.clicked.connect(self.resetRestrict)
        self.resetTrackerBtn.clicked.connect(self.resetTracker)
        self.saveFrameChkBox.stateChanged.connect(self.checkSaveFrame)

        self.videoTimer = VideoTimer()
        self.videoTimer.timeSignal.signal[str].connect(self.showVideoImages)

        self.infoTextBrowser.setFrameStyle(
            QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.infoTextBrowser.setFont(QtGui.QFont("Roman times", 15))
        self.infoTextBrowser.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    def closeEvent(self, event):
        accept = QtWidgets.QPushButton()
        cancel = QtWidgets.QPushButton()
        msg = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning, "關閉", "是否關閉！")
        msg.addButton(accept, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cancel, QtWidgets.QMessageBox.RejectRole)
        accept.setText("確定")
        cancel.setText("取消")
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            event.accept()

    def checkSaveFrame(self):
        logger.debug("Check box state changed")
        cbState = self.saveFrameChkBox.checkState()
        self.saveFrameCount = 0
        if cbState == QtCore.Qt.Checked:
            self.save = True
            self.datetime = getCurrentDatetime()
        elif cbState == QtCore.Qt.Unchecked:
            self.save = False

    def saveFrame(self, frame):
        saveFolder = os.path.join(save_frame_path, self.datetime)
        if not os.path.isdir(saveFolder):
            os.mkdir(saveFolder)
        cv2.imwrite(
            os.path.join(
                saveFolder,
                "f{:05d}.jpg".format(
                    self.saveFrameCount)),
            frame)
        self.saveFrameCount += 1

    def chooseFile(self):
        last_file_path = self.videoPath
        file_path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose File", current_path)
        video_path = last_file_path if file_path[0] == "" else file_path[0]
        self.resetTracker()
        self.setVideo(video_path, VIDEO_TYPE_OFFLINE)

    def setTimerFPS(self):
        global framePeroid
        fps = self.playCapture.get(cv2.CAP_PROP_FPS)
        framePeroid = 1 / fps
        self.videoTimer.setFPS(fps)
        logger.debug("Video FPS: {:.2f}".format(fps))

    def setVideo(self, path, videoType):
        self.resetVideo()
        self.videoPath = path
        self.videoType = videoType

    def resetVideo(self):
        """
        Reset to the beginning of the video
        """
        self.playCapture.release()
        self.videoPath = ""
        self.status = STATUS_INIT
        self.playBtn.setIcon(
            self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaPlay))

    def resetRestrict(self):
        """
        Clear the restrict area
        """
        self.poseDetect.restrict.reset()

    def resetTracker(self):
        """
        Reset Deep SORT Tracker, set track id to count from 1
        """
        resetTracker()

    def showVideoImages(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]
                self.videoLabel.resize(self.videoWidget.size())

                startTime = time.time()

                # Start Openpose
                datum = op.Datum()
                datum.cvInputData = frame
                self.opWrapper.emplaceAndPop([datum])

                self.poseDetect.setPoseKeypoints(datum.poseKeypoints, frame)
                self.poseDetect.poseStart()
                frame = self.poseDetect.getFrame()
                # frame = datum.cvOutputData

                if self.save:
                    self.saveFrame(frame)

                self.infoTextBrowser.setText(
                    self.poseDetect.getActionCountText())

                self.logTextBrowser.setText(str(getLogStream()))
                self.logTextBrowser.moveCursor(
                    self.logTextBrowser.textCursor().End)

                endTime = time.time()
                processTime = endTime - startTime
                logger.debug("Process time: {:.4f}".format(processTime))

                global framePeroid
                if processTime > framePeroid:
                    currentFPS = 1 / processTime
                else:
                    currentFPS = 1 / framePeroid
                cv2.putText(frame, "FPS: {:.2f}".format(currentFPS), (0, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                temp_image = QtGui.QImage(
                    rgb.flatten(), width, height, QtGui.QImage.Format_RGB888
                )
                temp_pixmap = QtGui.QPixmap.fromImage(temp_image)
                self.videoLabel.setPixmap(temp_pixmap)

                self.videoTimer.start()
            else:
                if self.videoType is VIDEO_TYPE_OFFLINE:
                    self.resetVideo()
                    self.playBtn.setIcon(
                        self.style().standardIcon(
                            QtWidgets.QStyle.SP_MediaStop))
                return
        else:
            self.resetVideo()

    def switchVideo(self):
        if self.status is STATUS_INIT:
            if self.videoPath == "":
                flag = self.playCapture.open(0)
            else:
                flag = self.playCapture.open(self.videoPath)

            self.setTimerFPS()
            self.videoTimer.start()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
            )
        elif self.status is STATUS_PLAYING:
            self.videoTimer.stop()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
            )
        elif self.status is STATUS_PAUSE:
            self.videoTimer.start()
            self.playBtn.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
            )

        self.status = (
            STATUS_PLAYING,
            STATUS_PAUSE,
            STATUS_PLAYING)[
            self.status]

    def startPaint(self):
        """
        Start paint restrict area
        """
        logger.info("Display OpenCV window for drawing restrict area")
        if self.poseDetect.getFrame() is None:
            return

        originFrame = self.poseDetect.getFrame()
        cv2.putText(originFrame,
                    "Press q to set and leave.",
                    (0, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    .8,
                    (0, 0, 255),
                    2)

        cv2.namedWindow("Restrict")
        cv2.setMouseCallback("Restrict", self.cv2PaintRestrict, originFrame)
        cv2.imshow("Restrict", originFrame)

        while True:
            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyWindow("Restrict")
                break

    def cv2PaintRestrict(self, event, x, y, flags, originFrame):
        """
        Define mouse event for an OpenCV window
        """
        global ix, iy, drawing
        paintFrame = originFrame.copy()

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            paintFrame = originFrame.copy()
            ix, iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                cv2.rectangle(
                    paintFrame,
                    (ix, iy),
                    (x, y),
                    (255, 255, 0),
                    2
                )
                cv2.imshow("Restrict", paintFrame)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            resCoord = (ix, iy, x, y)
            self.poseDetect.restrict.setRestrict(resCoord)
            logger.info(
                "Set Restrict area: [[{}, {}], [{}, {}]]".format(
                    ix, iy, x, y))
