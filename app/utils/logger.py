import gzip
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import threading

from app.utils.env_loader import LOG_NAME, LOG_DIR

_logger = None  # Global singleton


def get_env_variable(key: str, default: str = "") -> str:
    return os.getenv(key, default)


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        super().doRollover()
        log_filename = self.baseFilename + "." + datetime.now().strftime("%Y-%m-%d")
        compressed = log_filename + ".gz"
        if os.path.exists(log_filename):
            with open(log_filename, 'rb') as f_in:
                data = f_in.read()
            with gzip.open(compressed, 'wb') as f_out:
                f_out.write(data)
            os.remove(log_filename)


def get_logger(name: str = None) -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logger_name = name or LOG_NAME
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    logs_dir = Path(LOG_DIR)
    logs_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    def level_file_handler(level_name, level_obj):
        handler = logging.FileHandler(logs_dir / f"{logger_name}_{level_name}.log", encoding="utf-8")
        handler.setLevel(level_obj)
        handler.setFormatter(formatter)
        handler.addFilter(LevelFilter(level_obj))
        return handler

    # Main full log (rotating compressed)
    full_handler = CompressedTimedRotatingFileHandler(
        filename=logs_dir / f"{logger_name}.log",
        when="midnight",
        interval=1,
        backupCount=5,
        encoding="utf-8"
    )
    full_handler.setLevel(logging.DEBUG)
    full_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(full_handler)
    logger.addHandler(level_file_handler("info", logging.INFO))
    logger.addHandler(level_file_handler("warn", logging.WARNING))
    logger.addHandler(level_file_handler("error", logging.ERROR))
    logger.addHandler(level_file_handler("debug", logging.DEBUG))

    logger.propagate = False
    _logger = logger
    return _logger
