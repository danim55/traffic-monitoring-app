# --- configuration / labels ---
import logging
from typing import Sequence

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)