import time
import logging
from collections import deque
from datetime import datetime

class MemoryHandler(logging.Handler):
    def __init__(self, capacity=100):
        super().__init__()
        self.logs = deque(maxlen=capacity)

    def emit(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        }
        self.logs.append(log_entry)

    def get_logs(self):
        return list(self.logs)

# Setup memory logger
memory_handler = MemoryHandler()
memory_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
memory_handler.setFormatter(formatter)

def setup_memory_logging():
    root_logger = logging.getLogger()
    root_logger.addHandler(memory_handler)
