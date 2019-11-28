import tensorflow as tf
import numpy as np
import sys


def randomize(x, y):
    """ Randomizes the order of data samples and their corresponding labels"""
    permutation = np.random.permutation(y.shape[0])
    shuffled_x = x[permutation, :]
    shuffled_y = y[permutation]
    return shuffled_x, shuffled_y


def create_weight(name, shape):
    initer = tf.truncated_normal_initializer(mean=0, stddev=0.01)
    return tf.get_variable(
        "W_" + name,
        dtype=tf.float32,
        shape=shape,
        initializer=initer)


def create_bias(name, shape):
    initer = tf.constant(0, shape=shape, dtype=tf.float32)
    return tf.get_variable("b_" + name, dtype=tf.float32, initializer=initer)


def fc_layer(x, num_units, name, use_relu=True):
    in_dim = x.get_shape()[1]
    W = create_weight(name, shape=[in_dim, num_units])
    b = create_bias(name, [num_units])
    layer = tf.matmul(x, W)
    layer += b
    if use_relu:
        layer = tf.nn.relu(layer)
    return layer


def get_next_batch(x, y, start, end):
    x_batch = x[start:end]
    y_batch = y[start:end]
    return x_batch, y_batch


epochs = 400
batch_size = 500
display_freq = 100
learning_rate = 1e-4
h1 = 500
n_classes = 6
split_ratio = 0.9
keep_prob = 0.5

datasets = np.loadtxt(
    open(
        "./training_set.csv",
        "r"),
    delimiter=",")

X, y = datasets[:, 1:], datasets[:, 0]
del datasets

# one hot encoding for y
y = y.astype(int)
tmp = np.zeros((y.size, n_classes), dtype=int)
tmp[np.arange(y.size), y] = 1
y = tmp

training_size = int(y.shape[0] * split_ratio)

X_train, X_test = X[:training_size, :], X[training_size:, :]
y_train, y_test = y[:training_size], y[training_size:]
del X, y

print("X_trian shape: ", X_train.shape)
print("X_test shape: ", X_test.shape)
print("y_train shape: ", y_train.shape)
print("y_test shape:", y_test.shape)

X_test, y_test = randomize(X_test, y_test)

x = tf.placeholder(tf.float32, shape=[None, 50], name='X')
y = tf.placeholder(tf.float32, shape=[None, n_classes], name='Y')

fc1 = fc_layer(x, h1, 'FC1', use_relu=True)
fc1_d = tf.nn.dropout(fc1, rate=1 - keep_prob)
fc2 = fc_layer(fc1_d, h1, 'FC2', use_relu=True)
fc2_d = tf.nn.dropout(fc2, rate=1 - keep_prob)
fc3 = fc_layer(fc2_d, h1, 'FC3', use_relu=True)
fc3_d = tf.nn.dropout(fc3, rate=1 - keep_prob)
fc4 = fc_layer(fc3_d, h1, 'FC4', use_relu=True)
fc4_d = tf.nn.dropout(fc4, rate=1 - keep_prob)
fc5 = fc_layer(fc4_d, h1, 'FC5', use_relu=True)
fc5_d = tf.nn.dropout(fc5, rate=1 - keep_prob)
output_logits = fc_layer(fc5_d, n_classes, 'OUT', use_relu=False)

loss = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits_v2(
        labels=y, logits=output_logits),
    name='loss')
optimizer = tf.train.AdamOptimizer(
    learning_rate=learning_rate,
    name='Adam-op').minimize(loss)
correct_prediction = tf.equal(
    tf.argmax(
        output_logits, 1), tf.argmax(
            y, 1), name='correct_pred')
accuracy = tf.reduce_mean(
    tf.cast(
        correct_prediction,
        tf.float32),
    name='accuracy')
cls_prediction = tf.argmax(output_logits, axis=1, name='predictions')

loss_summary = tf.summary.scalar("Loss", loss)
acc_summary = tf.summary.scalar("Acc", accuracy)

merged = tf.summary.merge_all()
init = tf.global_variables_initializer()
saver = tf.train.Saver()

with tf.Session() as sess:
    sess.run(init)
    writer = tf.summary.FileWriter("./logs", sess.graph)
    num_tr_iter = int(len(y_train) / batch_size)
    X_train, y_train = randomize(X_train, y_train)
    X_test, y_test = randomize(X_test, y_test)
    global_step = 0

    for epoch in range(epochs):
        print('Training epoch: {}'.format(epoch + 1))
        for iteration in range(num_tr_iter):
            start = iteration * batch_size
            end = (iteration + 1) * batch_size
            x_batch, y_batch = get_next_batch(X_train, y_train, start, end)

            feed_dict_batch = {x: x_batch, y: y_batch}
            sess.run(optimizer, feed_dict=feed_dict_batch)
            summary = sess.run(merged, feed_dict=feed_dict_batch)
            writer.add_summary(summary, global_step)
            global_step += 1

            if iteration % display_freq == 0:
                loss_batch, acc_batch = sess.run([loss, accuracy],
                                                 feed_dict=feed_dict_batch)
                print(
                    "iter {0:3d}:\t Loss={1:.2f},\tTraining Accuracy={2:.01%}". format(
                        iteration, loss_batch, acc_batch))

        feed_dict_valid = {x: X_test, y: y_test}
        loss_valid, acc_valid = sess.run(
            [loss, accuracy], feed_dict=feed_dict_valid)
        print('---------------------------------------------------------')
        print(
            "Epoch: {0}, validation loss: {1:.2f}, validation accuracy: {2:.01%}". format(
                (epoch + 1),
                loss_valid,
                acc_valid))
        print('---------------------------------------------------------')

    # save_path = saver.save(sess, "./save_model/model")

    # Testing set acc
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
