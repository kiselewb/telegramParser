from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = BASE_DIR / "sessions"
LOGS_DIR = BASE_DIR / "logs"
LOGS_FILE = LOGS_DIR / "logs.log"
