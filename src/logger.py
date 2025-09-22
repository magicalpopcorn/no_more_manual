import logging
import shutil
import uuid
from datetime import datetime
from functools import partial
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .const import PROJECT_ROOT

# === Dynamically build today's timestamped log folder ===
_TMP_DIR = PROJECT_ROOT / "tmp" / "logs"
# Create a unique ID for this run
_run_id = str(uuid.uuid4())
LOG_FOLDER = _TMP_DIR / _run_id


# === Logger Setup ===
def action(label: str, detail: str = ""):
    n_dash = 20
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"{'-'*n_dash} {label.upper()} {'-'*n_dash}"
    # _tooltip(msg=f"{label}: {detail}")
    _logger.info(f"\n{header}\n[{timestamp}] {detail}")


def controller(msg, *args, **kwargs):
    _logger.info(f"[CONTROLLER] {msg}", *args, **kwargs)


# === Create and configure logger ===
_logger = logging.getLogger("rok_macro")
_logger.setLevel(logging.DEBUG)
_logger.propagate = False

debug = partial(_logger.debug)
info = partial(_logger.info)
warning = partial(_logger.warning)
error = partial(_logger.error)
critical = partial(_logger.critical)
exception = partial(_logger.exception)


def setup_logger(max_log_folders=3):

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
            log_file, maxBytes=200_000, backupCount=5, encoding="utf-8"
        )
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(formatter)
        _logger.addHandler(log_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
