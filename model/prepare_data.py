import numpy as np
import cv2
import sys
import os

sys.path.append("../")  # noqa
from src.utils import getActionLabel, scale_keypoints  # noqa


# Import Openpose
try:
    sys.path.append("../openpose/build/python")
    from openpose import pyopenpose as op
except ImportError as e:
    print("Error: OpenPose library could not be found.")
    raise e

params = dict()
params["model_folder"] = "../openpose/models"
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

datasets_path = "./datasets"
op_output_dir = "process_images"

problem_images = list()
action_list = getActionLabel("../action_label.txt")
action_dict = dict()


def process_images(save_image=False, mode="train"):
    all_keypoints = list()
    action_cat_dir = "train_images" if mode == "train" else "test_images"
    action_cat_path = os.path.join(datasets_path, mode, action_cat_dir)
    op_output_path = os.path.join(datasets_path, mode, op_output_dir)

    for dirName in os.listdir(action_cat_path):
        img_dir = os.path.join(action_cat_path, dirName)
        save_img_path = os.path.join(op_output_path, dirName)

        action_count = 0

        for file_ in os.listdir(img_dir):
            img_path = os.path.join(img_dir, file_)
            result = startOpenpose(img_path)

            if save_image:
                save_images(save_img_path, file_, result[2])

            if result[1].ndim != 0:
                keypoints = scale_keypoints(
                    result[0][0], result[0][1], result[1])

                for body in keypoints:
                    body = body.reshape((50))
                    label = action_list.index(dirName)
                    body = np.insert(body, 0, label, 0)
                    all_keypoints.append(body)
                    action_count += 1

                if result[1].shape[0] > 5:
                    problem_images.append(os.path.join(img_dir, file_))

            else:
                problem_images.append(os.path.join(img_dir, file_))
        action_dict[dirName] = action_count

    return np.array(all_keypoints)


def startOpenpose(img_path):
    frame = cv2.imread(img_path)

    if frame is None:
        print("Error in ", img_path)
        exit(1)

    # Start Openpose
    datum = op.Datum()
    datum.cvInputData = frame
    height, width = frame.shape[:2]
    opWrapper.emplaceAndPop([datum])
    print("Detect ", img_path)

    return [(height, width), datum.poseKeypoints, datum.cvOutputData]


def save_images(path, fileName, img):
    if not os.path.isdir(path):
        os.mkdir(path)
    cv2.imwrite(os.path.join(path, fileName), img)
    print("Saved ", path, fileName)


def write_csv(saveFile, keypoints):
    # Save as csv
    np.savetxt(saveFile, keypoints, fmt="%.4f", delimiter=",")
    print("Done saving training set")


def list_problem_images():
    if problem_images != []:
        print("\nSome images may have problem: ")
        for path in problem_images:
            print("\t", path)


if __name__ == "__main__":
    save_image = False
    mode = "train"
    output = "training_set.csv"

    if sys.argv[1] == "test":
        mode = "test"
        output = "testing_set.csv"
    if sys.argv[2] == "save":
        save_image = True

    training_set = process_images(save_image, mode)
    print(training_set.shape)
    write_csv(output, training_set)
    list_problem_images()
    print(action_dict)
