import cv2
import time
import numpy as np
import math
from collections import OrderedDict
from .restrict_area import Restrict
from .action import *
from .track import frameTrack
from ..utils import readConfig, getActionLabel
from ..logger import Logger

logger = Logger("pose_detect")
params = readConfig("./config.cfg", "App")
RESTRICT_AREA_THREAHOLD = float(params["restrict_area_threshold"])
BODY_POINTS_THRESHOLD = int(params["body_ponits_threshold"])


class Person:
    def __init__(self):
        self.keypoints = None
        self.box = None
        self.id = -1
        self.action = None
        self.inRestrict = False


class PoseDetect:
    def __init__(self):
        self.poseKeypoints = None
        self.poseBoxes = list()
        self.personList = list()
        self.frame = None
        self.restrict = Restrict(RESTRICT_AREA_THREAHOLD)
        self.actionCountText = ""
        self.actionCount = self.initActionCount()

    def initActionCount(self):
        tmpList = list()
        allAction = getActionLabel("./action_label.txt")
        for action in allAction:
            tmpList.append((action, 0))
        tmpList.append(("restrict", 0))
        return OrderedDict(tmpList)

    def getActionCountText(self):
        return self.actionCountText

    def setPoseKeypoints(self, poseKeypoints, frame):
        self.poseKeypoints = poseKeypoints
        self.frame = frame

    def setRestrict(self, restrict):
        """
        Give Restrict coordinate to restrict_area

        Parameter
        ----------
        restrict: tuple(x, y, diagonal x, diagonal y)
        """
        self.restrict.setRestrict(restrict)

    def resetPose(self):
        self.personList = list()
        self.poseBoxes = list()
        self.actionCount = self.initActionCount()

    def getFrame(self):
        return self.frame

    def checkKeypointsCount(self, idx):
        """
        Check whether poseKeypoints is more then
        {BODY_POINTS_THRESHOLD} points are non 0 or not.

        Parameter
        ----------
        idx: index of people

        Return Ture if more then {BODY_POINTS_THRESHOLD} points is non 0.
        """
        axisX = self.poseKeypoints[idx, :, 0]
        count = sum(val > 0 for val in axisX)
        return True if count >= BODY_POINTS_THRESHOLD else False

    def cleanBodypoints(self):
        """
        Clean self.poseKeypoints which less then
        {BODY_POINTS_THRESHOLD} body points.
        """
        people = self.poseKeypoints.shape[0]
        lst = list()
        for idx in range(people):
            if self.checkKeypointsCount(idx):
                lst.append(self.poseKeypoints[idx, :, :])
        if lst == []:
            lst = 0
        self.poseKeypoints = np.array(lst)

    def findBox(self, idx):
        """
        Find top left bottom right coordinate

        Parameter
        ----------
        idx: index of person

        Return
        ----------
        (top left x, top left y, bottom right x, bottom right y)
        """
        axisX = self.poseKeypoints[idx, :, 0]
        axisY = self.poseKeypoints[idx, :, 1]
        maxX = int(axisX.max())
        maxY = int(axisY.max())
        minX = int(axisX[axisX > 0].min())
        minY = int(axisY[axisY > 0].min())

        # minX = minX - 20 if minX - 20 > 0 else 2
        minY = minY - 20 if minY - 20 > 0 else 2
        return (minX, minY, maxX, maxY)

    def draw(self, minX, minY, maxX, maxY, msg, color=(0, 255, 0)):
        """
        Draw a bounding box where the person is and a label about his action

        Parameters
        ----------
        minX: top left x
        minY: top left y
        maxX: bottom right x
        maxY: bottom right y
        msg: text display
        color: (B, G, R)
        """
        cv2.rectangle(self.frame, (minX, minY), (maxX, maxY), color, 2)
        cv2.putText(
            self.frame,
            msg,
            (minX, minY),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

    def drawRestrict(self):
        if self.restrict.isSet():
            resX1, resY1, resX2, resY2 = self.restrict.getRestrict()
            self.draw(
                resX1, resY1, resX2, resY2, "", (0, 0, 255)
            )

    def drawBBox(self):
        """
        Draw all the bounding boxes on the frame
        """
        for person in self.personList:
            if person.id == -1:
                continue
            msg = "ID-{}[{}]".format(person.id, person.action)
            if person.inRestrict:
                logger.warning(
                    "WARNING ID-{} is inside Restrict Area".format(person.id))
                self.draw(
                    person.box[0],
                    person.box[1],
                    person.box[2],
                    person.box[3],
                    msg,
                    (0, 0, 255),
                )
            else:
                self.draw(
                    person.box[0],
                    person.box[1],
                    person.box[2],
                    person.box[3],
                    msg)

    def setActionCountText(self):
        self.actionCountText = ""
        for action in self.actionCount.items():
            self.actionCountText += "{:<12}\t: {}\n".format(
                action[0], action[1])
        self.actionCountText = self.actionCountText[:-1]

    def detect(self):
        """
        Detect every people in frame
        """
        height, width = self.frame.shape[:2]
        predictAction = actionDetect(self.poseKeypoints, height, width)
        for i in range(self.poseKeypoints.shape[0]):
            minX, minY, maxX, maxY = self.findBox(i)
            self.poseBoxes.append([minX, minY, maxX, maxY])

            person = Person()
            person.keypoints = self.poseKeypoints[i]
            person.box = [minX, minY, maxX, maxY]

            if self.restrict.isInside(
                    minX,
                    maxY - (maxY - minY) * 0.1,
                    maxX,
                    maxY) and self.restrict.isSet():
                resX1, resY1, resX2, resY2 = self.restrict.getRestrict()

                person.inRestrict = True
                person.action = "restrict"

                x = int((resX1 + resX2) / 2) - 65
                y = int((resY1 + resY2) / 2) + 15
                cv2.putText(
                    self.frame,
                    "WARNING",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )
            else:
                person.action = predictAction[i]

            self.actionCount[person.action] += 1
            self.personList.append(person)

        id_list, chk_list = frameTrack(self.poseBoxes, self.frame)
        for person in self.personList:
            # 原點到Box中心的歐式距離
            centX = (person.box[0] + person.box[2]) / 2
            centY = (person.box[1] + person.box[3]) / 2
            chk = math.sqrt(centX**2 + centY**2)
            try:
                idx = chk_list.index(min(chk_list, key=lambda x: abs(x - chk)))
                id_ = id_list[idx]
                del id_list[idx], chk_list[idx]
                person.id = id_
            except BaseException:
                person.id = -1
            # print("{} --- {}".format(id_, chk))

    def poseStart(self):
        # logger.debug("Pose Start")
        if self.poseKeypoints.ndim != 0:
            self.cleanBodypoints()

        if self.poseKeypoints.ndim != 0:
            self.detect()
            self.drawBBox()

        self.drawRestrict()
        self.setActionCountText()
        self.resetPose()
