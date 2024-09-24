
import tensorflow as tf
import keras.backend as KB
import keras as K
from keras.layers import Embedding, Input, Lambda, Normalization
from keras.optimizers.legacy import Adam
from keras.layers.experimental.preprocessing import TextVectorization
from .losses import contrastive_loss


def get_taxonomic_embedding_model(samples, embedding_size, compiled=False):
    data_input = Input(shape=(2,), dtype=tf.string)
    TV = TextVectorization(
        max_tokens=None,
        standardize=None,
        split=None,
        ngrams=None,
        output_mode="int",
        output_sequence_length=None,
        pad_to_max_tokens=False,
        vocabulary=tuple(samples),
        name='text_vectors'
    )
    initializer = tf.keras.initializers.RandomNormal(mean=0, stddev=0.3)
    E = Embedding(input_dim=len(samples) + 2,
                  output_dim=embedding_size,
                  embeddings_initializer=initializer,
                  name='embedding')
    N = Normalization()
    L2 = Lambda(lambda x: KB.sqrt(KB.sum(KB.square(x[0] - x[1]), axis=1)))

    taxa1_vecs = N(E(TV(data_input[:, 0])))
    taxa2_vecs = N(E(TV(data_input[:, 1])))
    normalized = [taxa1_vecs, taxa2_vecs]
    output = L2(normalized)

    adam = Adam()
    adam = tf.keras.mixed_precision.LossScaleOptimizer(adam)

    M = K.Model(data_input, output)

    if compiled:
        M.compile(loss=contrastive_loss, optimizer=adam)
    return M