# Pose Detection

A simple real-time human pose detection system based on [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose).

# Features

1. Human body keypoints detection via OpenPose.
2. Pose classification with a simple neural network.
   - Detected poses: stand, squat, sit, bend down, kneel, raise hand.
3. Each detected person is tracked using [Deep Sort](https://github.com/nwojke/deep_sort) algorithm.
4. PyQt5 UI.
