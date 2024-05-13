import os, sys, getopt, math
from os.path import dirname

import numpy as np
import struct
import json

import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import matplotlib

from naoth.LogReader import Parser
from naoth.LogReader import LogReader

from naoth.Representations_pb2 import TeamMessage


def parse(frame, number):
    if "TeamMessage" in frame.messages:
        msg = frame["TeamMessage"]
        robot = msg.data
        # frameInfo = frame["FrameInfo"]

        if len(msg.data) == 5:
            robot = msg.data[number - 1]
            return robot
        else:
            return None


def write(file, r, number, name):

    file.write(struct.pack("<i", number))
    file.write(name)
    file.write(b"\0")

    s = r.SerializeToString()
    # print len(s)
    file.write(struct.pack("<i", len(s)))
    file.write(s)


def export():
    myParser = Parser()

    logFilePath_5 = "../half1/150721-0952-Nao6022/game.log"
    logFilePath_4 = "../half1/150721-0952-Nao6026/game.log"
    logFilePath_3 = "../half1/150721-0953-Nao6043/game.log"
    logFilePath_2 = "../half1/150721-0955-Nao5862/game.log"
    logFilePath_1 = "../half1/150721-0954-Nao6035/game.log"

    readers = [0, 1, 2, 3, 4, 5]
    readers[0] = iter(LogReader(logFilePath_1, myParser))
    readers[1] = iter(LogReader(logFilePath_2, myParser))
    readers[2] = iter(LogReader(logFilePath_3, myParser))
    readers[3] = iter(LogReader(logFilePath_4, myParser))
    readers[4] = iter(LogReader(logFilePath_5, myParser))

    file = open("./test_head_rotation.log", "wb")

    fn = 1
    for i in range(1, 20000):

        msg = TeamMessage()
        frameInfo = None

        for j in range(0, 5):
            frame = next(readers[j])
            d = parse(frame, j + 1)
            if d != None:
                # HACK: store the head rotation in battery charge :P
                cm = frame["CameraMatrix"]
                d.user.batteryCharge = getRotationZ(cm)
                n = msg.data.extend([d])
                frameInfo = frame["FrameInfo"]

        if frameInfo != None:
            write(file, frameInfo, fn, "FrameInfo")
            write(file, msg, fn, "TeamMessage")
            fn += 1
            if fn % 100 == 0:
                print(fn)

    file.close()


def getRotationZ(cm):
    m = cm.pose
    h = np.sqrt(m.rotation[0].x * m.rotation[0].x + m.rotation[0].y * m.rotation[0].y)
    if h > 0:
        return np.arccos(m.rotation[0].x / h) * (-1 if m.rotation[0].y < 0 else 1)
    else:
        return 0


def test():
    myParser = Parser()

    logFilePath_5 = "../half1/150721-0952-Nao6022/game.log"
    logFilePath_4 = "../half1/150721-0952-Nao6026/game.log"
    logFilePath_3 = "../half1/150721-0953-Nao6043/game.log"
    logFilePath_2 = "../half1/150721-0955-Nao5862/game.log"
    logFilePath_1 = "../half1/150721-0954-Nao6035/game.log"

    readers = [0, 1, 2, 3, 4, 5]
    readers[0] = iter(LogReader(logFilePath_1, myParser))
    # readers[1] = iter(LogReader(logFilePath_2, myParser))
    # readers[2] = iter(LogReader(logFilePath_3, myParser))
    # readers[3] = iter(LogReader(logFilePath_4, myParser))
    # readers[4] = iter(LogReader(logFilePath_5, myParser))

    fn = 1
    for i in range(1, 200):

        msg = TeamMessage()
        frameInfo = None

        for j in range(0, 1):
            frame = next(readers[j])
            d = parse(frame, j + 1)
            if d != None:
                print(d.user.batteryCharge)
                n = msg.data.extend([d])
                frameInfo = frame["FrameInfo"]

        if frameInfo != None:
            cm = frame["CameraMatrix"]
            # print getRotationZ(cm)
            fn += 1
            if fn % 100 == 0:
                print(fn)


if __name__ == "__main__":

    # test()
    export()
