# ---------------- Config -----------------
import logging
import os
import queue
import threading
from typing import Any

from fastapi import FastAPI

HOST = os.getenv("DETECTOR_HOST", "0.0.0.0")
PORT = int(os.getenv("DETECTOR_PORT", "8080"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "2000"))  # bonded queue
WORKER_SLEEP = float(os.getenv("WORKER_SLEEP", "0.01"))  # tiny sleep to yield CPU

logger = logging.getLogger("detector")
logging.basicConfig(level=logging.INFO, format="%s(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="CICFlowMeter detector endpoint", version="0.1")

# Thread-safe bounded queue for incoming flows
flow_queue: queue.Queue[Any] = queue.Queue(maxsize=QUEUE_MAX_SIZE)
_stop_event: Any = threading.Event  # TODO assign correct type
_worker_thread: threading.Thread | None = None


def dummy_test_aux(value: int) -> int:
    return value


if __name__ == "__main__":
    print("Hello world")
