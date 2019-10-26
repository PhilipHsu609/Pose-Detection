import cv2
import sys
import numpy as np

from ..deep_sort.iou_matching import iou_cost
from ..deep_sort.kalman_filter import KalmanFilter
from ..deep_sort.tracker import Tracker
from ..deep_sort import nn_matching
from ..deep_sort.application_util import preprocessing
from ..deep_sort.linear_assignment import min_cost_matching
from ..deep_sort.detection import Detection
from ..deep_sort.tools import generate_detections as gdet

max_cosine_distance = 0.2
min_confidence = 0.5
nn_budget = 100
nms_max_overlap = 1.0
max_age = 30
n_init = 3

model_filename = "/home/ppcb/openpose/test/src/deep_sort/model/mars-small128.pb"
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric(
    "cosine", max_cosine_distance, nn_budget
)
tracker = Tracker(metric, max_age=max_age, n_init=n_init)

def resetTracker():
    tracker = Tracker(metric, max_age=max_age, n_init=n_init)

def frameTrack(poseBoxes, frame):
    currentFrame = frame

    boxes = np.array(poseBoxes)
    print(str(boxes))

    boxes_xywh = [[x1, y1, x2 - x1, y2 - y1] for [x1, y1, x2, y2] in boxes]

    features = encoder(currentFrame, boxes_xywh)
    detections = [
        Detection(bbox, 1.0, feature) for bbox, feature in zip(boxes_xywh, features)
    ]
    detections = [d for d in detections if d.confidence >= min_confidence]

    # Run non-maxima suppression.
    boxes_det = np.array([d.tlwh for d in detections])
    scores = np.array([d.confidence for d in detections])
    indices = preprocessing.non_max_suppression(boxes_det, nms_max_overlap, scores)
    detections = [detections[i] for i in indices]

    # Call the tracker
    tracker.predict()
    tracker.update(detections)

    id_list = []
    for track in tracker.tracks:
        id_list.append(track.track_id)

    return id_list
