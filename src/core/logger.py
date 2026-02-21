from datetime import datetime
from typing import List
from .storyteller import Storyteller

class GameLogger:
    def __init__(self, max_lines: int = 30):
        self.logs: List[str] = []
        self.max_lines = max_lines
        self.storyteller = Storyteller()
        self.emoji_map = {
            "⚖️": "COURT", "🕵️": "TAX", "😱": "ALARM", "✨": "GOLD", 
            "🤝": "GIFT", "💬": "TALK", "🌈": "GOOD", "💥": "CRISIS", 
            "🏗️": "BUILD", "🏘️": "TOWN", "🏰": "FORT", "🌍": "WORLD", 
            "📜": "LOG", "👥": "PEOPLE", "☀️": "DAY", "🌙": "NIGHT", 
            "🧘": "ZEN", "😊": "HAPPY", "😰": "STRESSED", "💀": "DEAD"
        }

    def log(self, message: str):
        # 1. Limpieza de emojis
        for emoji, text in self.emoji_map.items():
            message = message.replace(emoji, text)
            
        # 2. Narración (Embellecimiento)
        narrated_message = self.storyteller.narrate(message)
            
        timestamp = datetime.now().strftime("%H:%M")
        formatted_msg = f"[{timestamp}] {narrated_message}"
        self.logs.append(formatted_msg)
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)

    def get_logs(self) -> List[str]:
        return self.logs

logger = GameLogger(max_lines=30)
