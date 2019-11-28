import tensorflow as tf
import numpy as np
import sys

sys.path.append("../")  # noqa
from src.utils import scale_keypoints, getActionLabel  # noqa

actionLabel = getActionLabel("../action_label.txt")

gpu_options = tf.GPUOptions(allow_growth=True)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

saver = tf.train.import_meta_graph("./save_model/model.meta")
saver.restore(sess, "./save_model/model")

graph = tf.get_default_graph()
x = graph.get_tensor_by_name("X:0")
y = graph.get_tensor_by_name("Y:0")
predict = graph.get_tensor_by_name("predictions:0")
accuracy = graph.get_tensor_by_name("accuracy:0")

tf.reset_default_graph()


def actionDetect(keypoints, height, width):
    scalePoints = scale_keypoints(height, width, keypoints)
    inputData = list()
    for point in scalePoints:
        point = point.reshape((50))
        inputData.append(point)
    inputData = np.array(inputData)

    feed_dict = {x: inputData}
    output = sess.run(predict, feed_dict)

    result = list()
    for outputClass in output:
        result.append(actionLabel[outputClass])

    return result


# Testing
if __name__ == "__main__":
    datasets = np.loadtxt(
        open(
            "./testing_set.csv",
            "r"),
        delimiter=",")

    X_test, y_test = datasets[:, 1:], datasets[:, 0]
    del datasets

    # one hot encoding for y
    y_test = y_test.astype(int)
    tmp = np.zeros((y_test.size, 6), dtype=int)
    tmp[np.arange(y_test.size), y_test] = 1
    y_test = tmp

    acc = sess.run(accuracy, feed_dict={x: X_test, y: y_test})
    print("Acc: {:.02%}".format(acc))

    sess.close()
