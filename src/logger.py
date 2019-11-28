import logging
import os
from .utils import getCurrentDatetime


class LogStream:
    def __init__(self):
        self.logs = ""

    def write(self, msg):
        self.logs += msg
        if(len(self.logs) > 4000):
            self.logs = self.logs[2000:]
        # print(len(self.logs), "Bytes")

    def flush(self):
        pass

    def __str__(self):
        return self.logs


class Logger:
    def __init__(self, name=""):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        logFormat = "[%(asctime)s %(name)s] %(levelname)s : %(message)s"
        self.formatter = logging.Formatter(logFormat)
        self.streamHandler = logging.StreamHandler()
        self.saveStreamHandler = logging.StreamHandler(stream=log_stream)
        self.saveStreamHandler.setFormatter(self.formatter)
        self.streamHandler.setFormatter(self.formatter)
        path = os.path.join("./logs", (getCurrentDatetime() + ".log"))
        self.fileHandler = logging.FileHandler(filename=path)
        self.fileHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.streamHandler)
        self.logger.addHandler(self.saveStreamHandler)
        self.logger.addHandler(self.fileHandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def critical(self, msg):
        self.logger.critical(msg)


def getLogStream():
    return log_stream


log_stream = LogStream()
