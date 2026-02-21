from datetime import datetime
from typing import List

class GameLogger:
    def __init__(self, max_lines: int = 30):
        self.logs: List[str] = []
        self.max_lines = max_lines
        # Mapeo de emojis a texto ASCII para evitar romper curses
        self.emoji_map = {
            "⚖️": "COURT", "🕵️": "TAX", "😱": "ALARM", "✨": "GOLD", 
            "🤝": "GIFT", "💬": "TALK", "🌈": "GOOD", "💥": "CRISIS", 
            "🏗️": "BUILD", "🏘️": "TOWN", "🏰": "FORT", "🌍": "WORLD", 
            "📜": "LOG", "👥": "PEOPLE", "☀️": "DAY", "🌙": "NIGHT", 
            "🧘": "ZEN", "😊": "HAPPY", "😰": "STRESSED", "💀": "DEAD"
        }

    def log(self, message: str):
        # Limpiar emojis del mensaje
        for emoji, text in self.emoji_map.items():
            message = message.replace(emoji, text)
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.logs.append(formatted_msg)
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)

    def get_logs(self) -> List[str]:
        return self.logs

logger = GameLogger(max_lines=30)
