import logging
from pathlib import Path
from typing import Sequence, Tuple, Union, Optional

import joblib
import numpy as np
import pandas as pd
from keras import Sequential
from keras.src.layers import Flatten, Dropout, Dense, Conv1D, MaxPooling1D
from keras.src.saving import load_model
from tensorflow.python import keras

# --- Configuration / labels ---
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
) -> Sequential:
    """
    Build and compile the CNN used for traffic classification.
    Returns a compiled Sequential model (weights randomly initialized).
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


# --- Model loading helpers ---
def load_weights_to_model(model: Sequential, weights_path: Union[str, Path]) -> Sequential:
    """
    Load HDF5 weights into an existing model.
    """
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(f"Weights file not found: {weights_path}")
    model.load_weights(str(weights_path))
    logger.info("Loaded weights from %s", weights_path)
    return model


# --- Scaler helpers ---
def load_scaler(scaler_path: Union[str, Path]):
    """
    Load a fitted sklearn scaler (joblib or pickle).
    Example: joblib.dump(scaler, "scaler.pkl") at train time, then load here.
    """
    scaler_path = Path(scaler_path)
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
    scaler = joblib.load(str(scaler_path))
    logger.info("Loaded scaler from %s", scaler_path)
    return scaler


# --- Preprocessing + classification ---
def _clean_and_scale_array(
        x: np.ndarray, scaler
) -> np.ndarray:
    """
    Internal: clean NaN/inf and scale with provided scaler.
    Expects x shape: (n_samples, n_features).
    Returns scaled array (n_samples, n_features).
    """
    if not isinstance(x, np.ndarray):
        x = np.asarray(x, dtype=float)
    # replace inf/nan with -1 as original notebook did
    x = np.where(np.isfinite(x), x, -1.0).astype(float)
    # apply scaler
    x_scaled = scaler.transform(x)
    return x_scaled


def prepare_input_for_model(x_scaled: np.ndarray) -> np.ndarray:
    """
    Reshape scaled array for the model: (n_samples, n_features) -> (n_samples, n_features, 1)
    """
    return np.reshape(x_scaled, (x_scaled.shape[0], x_scaled.shape[1], 1))


def predict_labels_from_array(
        x: np.ndarray, model: keras.Model, scaler, labels: Optional[Sequence[str]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Classify a numpy array of features.
    Returns (predicted_indices, predicted_label_strings).
    - x: shape (n_samples, n_features) or convertible to it
    - model: compiled + loaded weights or full model
    - scaler: fitted sklearn scaler with transform()
    """
    if labels is None:
        labels = LABELS

    x_scaled = _clean_and_scale_array(x, scaler)
    x_input = prepare_input_for_model(x_scaled)
    probs = model.predict(x_input)
    pred_indices = np.argmax(probs, axis=-1)
    pred_labels = np.array([labels[i] for i in pred_indices])
    return pred_indices, pred_labels


def predict_labels_from_dataframe(
        df: pd.DataFrame, feature_columns: Optional[Sequence[str]], model: keras.Model, scaler,
        labels: Optional[Sequence[str]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Classify samples present in a pandas DataFrame.
    - df: DataFrame containing feature columns in the same order as used at training
    - feature_columns: list of the 77 feature column names in correct order.
        If None, will try to use the first DEFAULT_NUM_FEATURES numeric columns.
    """
    if feature_columns is None:
        # pick first numeric columns up to DEFAULT_NUM_FEATURES
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_columns = numeric_cols[:DEFAULT_NUM_FEATURES]
        if len(feature_columns) != DEFAULT_NUM_FEATURES:
            raise ValueError("Could not infer feature columns automatically; please pass feature_columns explicitly.")

    x = df[list(feature_columns)].values.astype(float)
    return predict_labels_from_array(x, model, scaler, labels=labels)


# --- Convenience: load model+scaler and run on DataFrame/file ---
def load_model_and_scaler(weights_path: Optional[Union[str, Path]] = None,
                          saved_model_path: Optional[Union[str, Path]] = None,
                          scaler_path: Optional[Union[str, Path]] = None
                          ) -> Tuple[Sequential, object]:
    """
    Convenience helper:
    - Provide `weights_path` together with a freshly built model.
    - scaler_path should point to a joblib/pickle dump of the scaler used at training time.
    Returns (model, scaler).
    """
    model = build_detector()
    if weights_path is None:
        raise ValueError(
            "If saved_model_path is not provided, weights_path must be provided to load weights into a freshly built model.")
    load_weights_to_model(model, weights_path)

    if scaler_path is None:
        raise ValueError("scaler_path must point to the fitted scaler used at training time (joblib file).")
    scaler = load_scaler(scaler_path)
    return model, scaler
