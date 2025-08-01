import logging
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.const import PROJECT_ROOT

# === Dynamically build today's timestamped log folder ===
_date_str = datetime.now().strftime("%Y-%m-%d")
_time_str = datetime.now().strftime("%H-%M-%S")

_TMP_DIR = PROJECT_ROOT / "tmp" / "logs"
LOG_FOLDER = _TMP_DIR / _date_str / _time_str


# === Logger Setup ===
def action(label: str, detail: str = ""):
    n_dash = 20
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"{"-"*n_dash} {label.upper()} {"-"*n_dash}"
    # _tooltip(msg=f"{label}: {detail}")
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


# TODO: remove or replace
def _tooltip(msg, x=900, y=-25):
    pass
    # AHK_API.show_tooltip(str(msg), x, y)


# === Create and configure logger ===
_logger = logging.getLogger("rok_macro")
_logger.setLevel(logging.DEBUG)
_logger.propagate = False


def setup_logger(max_log_folders=4):
    # Cleanup old logs
    def _cleanup_old_logs(root_dir: Path, max_folders: int):
        if not root_dir.exists():
            return
        dated_folders = sorted(root_dir.glob("*/*"), key=lambda f: f.stat().st_mtime, reverse=True)
        for old_folder in dated_folders[max_folders:]:
            shutil.rmtree(old_folder, ignore_errors=True)

    _cleanup_old_logs(_TMP_DIR, max_folders=max_log_folders)
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)
    log_file = LOG_FOLDER / "macro.log"

    if not _logger.hasHandlers():
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        log_handler = RotatingFileHandler(
            log_file, maxBytes=50_000, backupCount=5, encoding="utf-8"
        )
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(formatter)
        _logger.addHandler(log_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)

    info(f"Log saved at: {log_file}")
