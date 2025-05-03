import os
import threading
import time
from pathlib import Path
from app.utils.logger import get_logger
from app.utils.env_loader import LOG_NAME, LOG_DIR

def log_from_thread(index):
    logger = get_logger()
    logger.info(f"[Thread-{index}] test log from thread.")

def test_threaded_logging_writes_to_rotated_file():
    logger = get_logger()

    threads = []
    for i in range(5):
        t = threading.Thread(target=log_from_thread, args=(i,), name=f"Thread-{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Allow file handlers to flush
    time.sleep(0.5)

    full_log_path = Path(LOG_DIR) / f"{LOG_NAME}.log"
    assert full_log_path.exists(), f"Expected log file not found: {full_log_path}"

    with open(full_log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        for i in range(5):
            assert f"[Thread-{i}]" in content, f"Thread-{i} log not found in {full_log_path.name}"
