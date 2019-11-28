import cv2
import sys
import numpy as np
import math
from ..utils import readConfig
from ..deep_sort.iou_matching import iou_cost
from ..deep_sort.kalman_filter import KalmanFilter
from ..deep_sort.tracker import Tracker
from ..deep_sort import nn_matching
from ..deep_sort.application_util import preprocessing
from ..deep_sort.linear_assignment import min_cost_matching
from ..deep_sort.detection import Detection
from ..deep_sort.tools import generate_detections as gdet

# Read Deep SORT Config
params = readConfig("./config.cfg", "DeepSORT")
MAX_CONSINE_DISTANCE = float(params["max_cosine_distance"])
MIN_CONFIDENCE = float(params["min_confidence"])
NN_BUDGET = int(params["nn_budget"])
NMS_MAX_OVERLAP = float(params["nms_max_overlap"])
MAX_AGE = int(params["max_age"])
N_INIT = int(params["n_init"])
MODEL_FILE = params["model_file"]

encoder = gdet.create_box_encoder(MODEL_FILE, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric(
    "cosine", MAX_CONSINE_DISTANCE, NN_BUDGET
)
tracker = Tracker(metric, max_age=MAX_AGE, n_init=N_INIT)


def resetTracker():
    global tracker
    tracker = Tracker(metric, max_age=MAX_AGE, n_init=N_INIT)


def frameTrack(poseBoxes, frame):
    boxes = np.array(poseBoxes)

    boxes_xywh = [[x1, y1, x2 - x1, y2 - y1] for [x1, y1, x2, y2] in boxes]

    features = encoder(frame, boxes_xywh)
    detections = [Detection(bbox, 1.0, feature)
                  for bbox, feature in zip(boxes_xywh, features)]
    detections = [d for d in detections if d.confidence >= MIN_CONFIDENCE]

    # Run non-maxima suppression.
    boxes_det = np.array([d.tlwh for d in detections])
    scores = np.array([d.confidence for d in detections])
    indices = preprocessing.non_max_suppression(
        boxes_det, NMS_MAX_OVERLAP, scores)
    detections = [detections[i] for i in indices]

    # Call the tracker
    tracker.predict()
    tracker.update(detections)

    id_list = list()
    chk_list = list()
    for track in tracker.tracks:
        # if track.is_confirmed() or track.time_since_update > 1:
        #     continue

        bbox = track.to_tlbr()

        # 原點到Box中心的歐式距離
        centX = (bbox[0] + bbox[2]) / 2
        centY = (bbox[1] + bbox[3]) / 2
        chk = math.sqrt(centX**2 + centY**2)

        id_list.append(track.track_id)
        chk_list.append(chk)
        # print("{} --- {}".format(track.track_id, chk))

    return id_list, chk_list
