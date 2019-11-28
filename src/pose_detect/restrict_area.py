class Restrict:
    def __init__(self, areaThreshold: float = 0.8):
        self.resIsSet = False
        self.resX1 = 0
        self.resY1 = 0
        self.resX2 = 0
        self.resY2 = 0
        self.restrictThresh = areaThreshold

    def setRestrict(self, restrict):
        self.resIsSet = True
        self.resX1 = restrict[0]
        self.resY1 = restrict[1]
        self.resX2 = restrict[2]
        self.resY2 = restrict[3]
        self.toTLBR()

    def toTLBR(self):
        """
        To top left buttom right
        """
        minX, minY = min(self.resX1, self.resX2), min(self.resY1, self.resY2)
        maxX, maxY = max(self.resX1, self.resX2), max(self.resY1, self.resY2)
        self.resX1 = minX
        self.resY1 = minY
        self.resX2 = maxX
        self.resY2 = maxY

    def isSet(self):
        return self.resIsSet

    def reset(self):
        self.resIsSet = False
        self.resX1 = 0
        self.resY1 = 0
        self.resX2 = 0
        self.resY2 = 0

    def getRestrict(self):
        return (self.resX1, self.resY1, self.resX2, self.resY2)

    def isInside(self, x1, y1, x2, y2):
        personArea = (x2 - x1) * (y2 - y1)

        xmin = min(x2, self.resX2)
        xmax = max(x1, self.resX1)
        ymin = min(y2, self.resY2)
        ymax = max(y1, self.resY1)

        width = xmin - xmax
        height = ymin - ymax

        if width <= 0 or height <= 0:
            return False

        crossArea = width * height
        ratio = crossArea / personArea

        # print("RATIO: ", ratio)

        return True if ratio >= self.restrictThresh else False
