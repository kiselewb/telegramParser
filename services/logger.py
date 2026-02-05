import logging
import colorlog
import sys
from pathlib import Path
from config.paths import LOGS_DIR, LOGS_FILE


class Logger:
    def __init__(
        self,
        name: str,
        level: int = logging.DEBUG,
        log_file: Path | str | None = LOGS_FILE,
        is_console_log: bool = True,
    ):
        self.name = name
        self.level = level
        self.log_file = log_file
        self.is_console_log = is_console_log

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.handlers.clear()

        formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s | %(levelname)-8s%(reset)s | %(cyan)s%(name)-36s%(reset)s | %(blue)s%(filename)-24s%(reset)s | %(message_log_color)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={
                "message": {
                    "DEBUG": "white",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                }
            },
        )

        if self.is_console_log:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if self.log_file:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger
