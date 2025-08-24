# --- configuration / labels ---
import logging
from typing import Sequence, Tuple

import tensorflow as tf
from keras import Sequential
from keras.src.layers import Flatten, Dropout, Dense, Conv1D, MaxPooling1D

LABELS: Sequence[str] = [
    "Benign",
    "DoS attacks-GoldenEye",
    "DoS attacks-Hulk",
    "DoS attacks-SlowHTTPTest",
    "DoS attacks-Slowloris",
    "FTP-BruteForce",
    "SSH-Bruteforce",
]

DEFAULT_NUM_FEATURES = 77
DEFAULT_INPUT_SHAPE = (DEFAULT_NUM_FEATURES, 1)
NUM_CLASSES = len(LABELS)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.info("started")


# ------ Model creation ------
def build_detector(
        input_shape: Tuple[int, int] = DEFAULT_INPUT_SHAPE,
        num_classes: int = NUM_CLASSES,
) -> tf.keras.Model:
    """
    Build and compile the CNN used for traffic classification.
    Returns a compiled tf.keras.Model (weights randomly initialized).
    """
    model = Sequential(name="cnn_detector")

    # 1D convolution block 1
    model.add(Conv1D(filters=64, kernel_size=3, activation="relu", padding="same", input_shape=input_shape))
    model.add(Conv1D(filters=64, kernel_size=3, activation="relu", padding="same"))
    model.add(MaxPooling1D(pool_size=2))

    # 1D convolution block 2
    model.add(Conv1D(filters=128, kernel_size=3, activation="relu", padding="same"))
    model.add(Conv1D(filters=128, kernel_size=3, activation="relu", padding="same"))
    model.add(MaxPooling1D(pool_size=2))

    # Classification head
    model.add(Flatten())
    model.add(Dropout(0.1))
    model.add(Dense(num_classes, activation="softmax"))

    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["categorical_accuracy"],
    )
    logger.info("Built CNN model with input_shape=%s and num_classes=%d", input_shape, num_classes)
    return model
