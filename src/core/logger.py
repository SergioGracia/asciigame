from datetime import datetime
from typing import List

class GameLogger:
    def __init__(self, max_lines: int = 30):
        self.logs: List[str] = []
        self.max_lines = max_lines

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.logs.append(formatted_msg)
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)

    def get_logs(self) -> List[str]:
        return self.logs

# Instancia global para facilitar el acceso desde las entidades
logger = GameLogger(max_lines=30)
