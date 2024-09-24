import tensorflow as tf
import tensorflow.keras.backend as KB


def contrastive_loss(y_true, y_pred, margin=1):
    # explicitly cast the true class label data type to the predicted
    # class label data type (otherwise we run the risk of having two
    # separate data types, causing TensorFlow to error out)
    y_true = tf.cast(y_true, y_pred.dtype)

    # calculate the contrastive loss between the true labels and
    # the predicted labels
    squaredPreds = KB.square(y_pred)
    squaredMargin = KB.square(KB.maximum(margin - y_pred, 0))
    # Calculate squared margin without limitations for cosine sim
    return KB.mean((1 - y_true) * squaredPreds + y_true * squaredMargin)