import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from src.ahk import AHK_API
from src.const import PROJECT_ROOT

# === Dynamically build today's timestamped log folder ===
_date_str = datetime.now().strftime("%Y-%m-%d")
_time_str = datetime.now().strftime("%H-%M-%S")

_TMP_DIR = PROJECT_ROOT / "tmp" / "logs"
LOG_FOLDER = _TMP_DIR / _date_str / _time_str


LOG_FOLDER.mkdir(parents=True, exist_ok=True)

_LOG_FILE = LOG_FOLDER / "macro.log"
_ERR_FILE = LOG_FOLDER / "error.log"


# === Logger Setup ===
def action(label: str, detail: str = ""):
    n_dash = 20
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"{"-"*n_dash} {label.upper()} {"-"*n_dash}"
    _tooltip(msg=f"{label}: {detail}")
    _logger.info(f"\n{header}\n[{timestamp}] {detail}")


def controller(msg, *args, **kwargs):
    _logger.info(f"[CONTROLLER] {msg}", *args, **kwargs)


def debug(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.critical(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    _tooltip(msg)
    _logger.exception(msg, *args, **kwargs)


def _tooltip(msg, x=900, y=-25):
    AHK_API.show_tooltip(str(msg), x, y)


# === Create and configure logger ===
_logger = logging.getLogger("rok_macro")
_logger.setLevel(logging.DEBUG)

if not _logger.hasHandlers():
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    log_handler = RotatingFileHandler(_LOG_FILE, maxBytes=500_000, backupCount=5, encoding="utf-8")
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(formatter)
    _logger.addHandler(log_handler)

    err_handler = RotatingFileHandler(_ERR_FILE, maxBytes=500_000, backupCount=3, encoding="utf-8")
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)
    _logger.addHandler(err_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(console_handler)
