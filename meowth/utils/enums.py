from enum import Enum

class ExitCodes(Enum):
    SHUTDOWN = 0
    CRITICAL = 1
    RESTART = 26
    