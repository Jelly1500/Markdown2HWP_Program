import os
import sys
import datetime

LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "md2hwp_debug.log"

_initialized = False
_log_file_path = None


def _ensure_initialized():
    global _initialized, _log_file_path
    if _initialized:
        return
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        log_dir = os.path.join(base_dir, LOG_DIR_NAME)
        os.makedirs(log_dir, exist_ok=True)
        _log_file_path = os.path.join(log_dir, LOG_FILE_NAME)
        _initialized = True
    except Exception:
        # 폴더 생성 실패 시 프로젝트 루트에 직접 기록 시도
        _log_file_path = os.path.abspath(LOG_FILE_NAME)
        _initialized = True


def _write(level: str, message: str):
    _ensure_initialized()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{ts}] [{level}] {message}"
    try:
        with open(_log_file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # 파일 기록 실패 시 표준 출력으로만
        pass
    print(line)
    sys.stdout.flush()


def log_debug(msg: str):
    _write("DEBUG", msg)


def log_info(msg: str):
    _write("INFO", msg)


def log_warn(msg: str):
    _write("WARN", msg)


def log_error(msg: str):
    _write("ERROR", msg)


