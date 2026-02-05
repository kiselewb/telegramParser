from enum import Enum


class ProcessedMessageStatus(Enum):
    waiting = "waiting"
    sent = "sent"
    error = "error"
