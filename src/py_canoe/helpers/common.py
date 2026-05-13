import os
import sys
import time
import logging
import pythoncom
from datetime import datetime
from pathlib import Path

def check_if_path_exists(path: str, create_if_not_exist: bool=False) -> bool:
    """Check if a given path exists. Optionally create it if it doesn't."""
    if os.path.exists(path):
        return True
    else:
        if create_if_not_exist:
            try:
                os.makedirs(path, exist_ok=True)
                return True
            except Exception as e:
                logger.error(f"Error creating directory {path}: {e}")
                return False
        else:
            return False

def setup_logger(name='py_canoe', filename='py_canoe.log'):
    """Set up and return a logger with console and file handlers."""
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fmt = "%(asctime)s [PY_CANOE] [%(levelname)-4.8s] %(message)s"
    # Add console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(console_handler)
    logger.propagate = False
    return logger

def update_logger_file_path(logger: logging.Logger, log_dir_path: str | Path) -> None:
    """Update the file handler of an existing logger to a new file path."""
    new_filename = os.path.join(log_dir_path, 'py_canoe.log')
    if check_if_path_exists(os.path.dirname(new_filename), create_if_not_exist=True):
        # Remove existing FileHandlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                handler.close()
        # Add new FileHandler
        fmt = "%(asctime)s [PY_CANOE] [%(levelname)-4.8s] %(message)s"
        file_handler = logging.FileHandler(new_filename, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)
    else:
        logger.error(f"Cannot update logger file path. Directory does not exist and could not be created: {os.path.dirname(new_filename)}")


logger = setup_logger()

def wait(timeout_seconds=0.1):
    """Pump waiting COM messages and sleep for the given timeout."""
    pythoncom.PumpWaitingMessages()
    time.sleep(timeout_seconds)

def DoEvents() -> None:
    wait(0.01)

def DoEventsUntil(cond, timeout, title) -> bool:
    base_time = datetime.now()
    while not cond():
        DoEvents()
        now = datetime.now()
        difference = now - base_time
        seconds = difference.seconds
        if seconds > timeout:
            logger.warning(f'{title} timeout({timeout} s)')
            return False
    return True
