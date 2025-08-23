# ---------------- Config -----------------
import logging
import os
import queue
import threading
import time
from http.client import HTTPException
from typing import Any, Dict, Union
from urllib.request import Request

import uvicorn
from fastapi import FastAPI
from starlette.responses import JSONResponse

HOST = os.getenv("DETECTOR_HOST", "0.0.0.0")
PORT = int(os.getenv("DETECTOR_PORT", "8080"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "2000"))  # bonded queue
WORKER_SLEEP = float(os.getenv("WORKER_SLEEP", "0.01"))  # tiny sleep to yield CPU
CONTENT_TYPE = "content-type"

logger = logging.getLogger("detector")
logging.basicConfig(level=logging.INFO, format="%s(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="CICFlowMeter detector endpoint", version="0.1")

# Thread-safe bounded queue for incoming flows
flow_queue: queue.Queue[Any] = queue.Queue(maxsize=QUEUE_MAX_SIZE)
_stop_event: type = threading.Event  # TODO assign correct type
_worker_thread: threading.Thread | None = None


def dummy_test_aux(value: int) -> int:
    return value


def process_flow_item(item: Union[Dict[str, Any], list]) -> None:
    """
    Replace this with actual preprocessing + model inference.
    Keep it fast and non-blocking; heavy work should be delegated to a pool or separate service.
    :param item: flow to be processed
    """
    # Basic example: log the most useful fields if present
    flow_id = None
    if isinstance(item, dict):
        flow_id = item.get("Flow Id")
    logger.info("Processing flow (Flow Id = %s keys=%s", flow_id, list(item.keys()))


def _worker_loop():
    logger.info("Worker trhead started (queue maxsize=%d)", QUEUE_MAX_SIZE)
    while not _stop_event.is_set():
        try:
            item = flow_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        try:
            process_flow_item(item)
        except Exception as e:
            logger.exception("Error processing flow: %s", e)
        finally:
            try:
                flow_queue.task_done()
            except Exception:
                pass
        # Gentle sleep to avoid busy-loop spikes
        time.sleep(WORKER_SLEEP)

    logger.info("Worker thread stopping")


@app.post("/predict")
async def predict(payload: Union[Dict[str, Any], list, Any], request: Request):
    """
    Expected: CICFlowMeter POSTs a single flow as JSON.
    We accept dict or list; we simply enqueue the payload for background processing.
    Returns 200 on enqueue or 503 if queue is full
    :param payload: received flow from CICFlowMeter
    :param request: Request from the server
    :return: JSONResponse with 200 if succeed or 503 if queue is full
    """
    # First we check if the received information is in JSON format
    if request.headers.get(CONTENT_TYPE, "").lower().find("application/json") < 0:
        logger.debug("Non-JSON content type: %s", request.headers.get(CONTENT_TYPE))

    # Second, enqueue or return 503 if full
    try:
        flow_queue.put_nowait(payload)
    except queue.Full:
        logger.warning("Queue full, rejecting flow")
        raise HTTPException(status_code=503, detail="ingestion queue full")

    # Immediately ack; processing happens async
    return JSONResponse({"status": "received"}, status_code=200)


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "queue_length": flow_queue.qsize()}


def _run():
    # Call uvicorn programmatically so Dockerfile command keeps being valid
    uvicorn.run("detector.main:app", host=HOST, port=PORT, log_level="info", reload=True)


if __name__ == "__main__":
    _run()
