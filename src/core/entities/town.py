from .base import Entity
from ..logger import logger

class Town(Entity):
    def __init__(self, name: str, x: int = 0, y: int = 0):
        super().__init__(name, x, y)
        self.wood_stock = 0
        self.level = 1
        self.level_names = {1: "Choza", 2: "Refugio", 3: "Fortaleza", 4: "Ciudadela"}

    def add_wood(self, amount: int):
        self.wood_stock += amount
        old_level = self.level
        if self.wood_stock >= 50: self.level = 2
        if self.wood_stock >= 200: self.level = 3
        if self.wood_stock >= 500: self.level = 4
        
        if self.level > old_level:
            logger.log(f"🏗️ ¡{self.name} ha subido al nivel {self.level} ({self.level_names[self.level]})!")

    def __repr__(self):
        return f"<Town {self.name} Lvl:{self.level} Wood:{self.wood_stock}>"
