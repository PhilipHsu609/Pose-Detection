import tensorflow as tf
import numpy as np
from ..utils import scale_keypoints, getActionLabel

actionLabel = getActionLabel("./action_label.txt")

gpu_options = tf.GPUOptions(allow_growth=True)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

saver = tf.train.import_meta_graph("./model/save_model/model.meta")
saver.restore(sess, "./model/save_model/model")

graph = tf.get_default_graph()
x = graph.get_tensor_by_name("X:0")
predict = graph.get_tensor_by_name("predictions:0")

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
# if __name__ == "__main__":
#     x = np.arange(50).reshape((1, 25, 2))
#     result = actionDetect(x, 300, 300)
#     print(result)
