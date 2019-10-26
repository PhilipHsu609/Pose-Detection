import cv2
import time
import numpy as np
from .restrict_area import Restrict
from .action import *
from .track import frameTrack


class Person:
    def __init__(self):
        self.keypoints = None
        self.box = None
        self.id = -1
        self.action = ""
        self.inRestrict = False


class PoseDetect:
    def __init__(self):
        self.poseKeypoints = None
        self.poseBoxes = []
        self.personList = []
        self.frame = None
        self.restrict = Restrict()
        self.actionText = "stand"
        self.actionCountText = ""
        self.actionCount = {
            "sit": 0,
            "kneel": 0,
            "squat": 0,
            "benddown": 0,
            "raisehand": 0,
            "stand": 0,
            "restrict": 0,
        }

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
        self.personList = []
        self.poseBoxes = []
        self.actionCount = {
            "sit": 0,
            "kneel": 0,
            "squat": 0,
            "benddown": 0,
            "raisehand": 0,
            "stand": 0,
            "restrict": 0,
        }

    def getFrame(self):
        return self.frame

    def checkKeypointsCount(self, idx):
        """
        Check poseKeypoints is more then 10 points.
        Return Ture if more then 10 points is 0.
        """
        count = 0
        for i in range(25):
            if self.poseKeypoints[idx, i, 0] == 0:
                count += 1
        return False if count < 20 else True

    def cleanBodypoints(self):
        """
        Clean self.poseKeypoints which less then 10 body points
        """
        people = self.poseKeypoints.shape[0]
        check = [True for _ in range(people)]

        for idx in range(people):
            if self.checkKeypointsCount(idx):
                check[idx] = False

        self.poseKeypoints = self.poseKeypoints[check]

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
        maxX = 0
        maxY = 0
        minX = 1e4
        minY = 1e4
        arr = self.poseKeypoints
        for i in range(25):
            if arr[idx, i, 0] != 0:
                if arr[idx, i, 0] < minX:
                    minX = arr[idx, i, 0]
                if arr[idx, i, 0] > maxX:
                    maxX = arr[idx, i, 0]
            if arr[idx, i, 1] != 0:
                if arr[idx, i, 1] < minY:
                    minY = arr[idx, i, 1]
                if arr[idx, i, 1] > maxY:
                    maxY = arr[idx, i, 1]
        return (minX, minY, maxX, maxY)

    def drawBox(self, minX, minY, maxX, maxY, msg, color=(0, 255, 0)):
        """
        Draw a box where the person is and a label about his action

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
            1,
            (255, 255, 255),
            2,
        )

    def draw(self):
        """
        Draw boxes on the frame
        """
        for person in self.personList:
            msg = "ID-{}[{}]".format(person.id, person.action)
            if person.inRestrict:
                self.drawBox(
                    person.box[0],
                    person.box[1],
                    person.box[2],
                    person.box[3],
                    msg,
                    (0, 0, 255),
                )
            else:
                self.drawBox(
                    person.box[0], person.box[1], person.box[2], person.box[3], msg
                )

    def setActionCountText(self):
        self.actionCountText = ""
        for i in self.actionCount.items():
            self.actionCountText += str(i[0]) + "\t:" + str(i[1]) + "\n"

    def detect(self):
        """
        Detect every person in a frame
        """
        for i in range(self.poseKeypoints.shape[0]):
            minX, minY, maxX, maxY = self.findBox(i)
            self.poseBoxes.append([minX, minY, maxX, maxY])
            arr = self.poseKeypoints

            person = Person()
            person.keypoints = self.poseKeypoints[i]
            person.box = [minX, minY, maxX, maxY]

            if self.restrict.isInside(minX, minY, maxX, maxY) and self.restrict.isSet():
                resX1, resY1, resX2, resY2 = self.restrict.getRestrict()

                person.inRestrict = True
                person.action = "restrict"

                x = int((resX1 + resX2) / 2) - 30
                y = int((resY1 + resY2) / 2)
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
                if kneel(arr, i):
                    person.action = "kneel"
                elif sitCalf(arr, i, maxY, minY):
                    person.action = "sit"
                elif squat(arr, i, maxY, minY):
                    person.action = "squat"
                elif sit3(arr, i):
                    person.action = "sit"
                elif squat2(arr, i):
                    person.action = "squat"
                elif sit2(arr, i):
                    person.action = "sit"
                elif benddown(arr, i):
                    person.action = "benddown"
                elif raisehand(arr, i):
                    person.action = "raisehand"
                else:
                    person.action = "stand"

            self.actionCount[person.action] += 1
            self.personList.append(person)

        id_list = frameTrack(self.poseBoxes, self.frame)
        for person, id_ in zip(self.personList, id_list):
            person.id = id_

    def poseStart(self):
        if self.poseKeypoints.ndim != 0:
            self.cleanBodypoints()

        if self.poseKeypoints.ndim != 0:
            self.detect()
            self.draw()

        self.setActionCountText()
        self.resetPose()
