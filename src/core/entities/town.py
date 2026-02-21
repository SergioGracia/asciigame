from .base import Entity
from ..logger import logger

class Town(Entity):
    def __init__(self, name: str, x: int = 0, y: int = 0, owner_name: str = "Sistema"):
        super().__init__(name, x, y)
        self.owner_name = owner_name
        self.residents = [owner_name]
        self.wood_stock = 0
        self.level = 1
        self.max_residents = 2
        
        self.dims = {1: 3, 2: 5, 3: 7, 4: 9, 5: 13}
        self.tiles = {}
        self._update_structure()

    def add_resident(self, name: str):
        if len(self.residents) < self.max_residents:
            self.residents.append(name)
            return True
        return False

    def add_wood(self, amount: int):
        self.wood_stock += amount
        # Si la casa está llena, necesita expandirse para albergar más gente
        if self.wood_stock >= (self.level * 50):
            self.upgrade()

    def _update_structure(self):
        self.tiles = {}
        size = self.dims[self.level]
        half = size // 2
        # Formas distintas según el nivel
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                is_edge = abs(dx) == half or abs(dy) == half
                if is_edge:
                    if dy == half and dx == 0:
                        self.tiles[(dx, dy)] = {"char": "+", "solid": False, "type": "DOOR"}
                    else:
                        self.tiles[(dx, dy)] = {"char": "X", "solid": True, "type": "WALL"}
                else:
                    self.tiles[(dx, dy)] = {"char": " ", "solid": False, "type": "INTERIOR"}

    def upgrade(self):
        if self.level < 5:
            self.level += 1
            self.max_residents += 1
            self._update_structure()
            logger.log(f"BUILD: La casa de {self.owner_name} ha sido ampliada a Nivel {self.level}.")

    def is_inside(self, x, y):
        rel_x, rel_y = int(x - self.x), int(y - self.y)
        return (rel_x, rel_y) in self.tiles and self.tiles[(rel_x, rel_y)]["type"] == "INTERIOR"

    def get_tile_at(self, x, y):
        rel_x, rel_y = int(x - self.x), int(y - self.y)
        return self.tiles.get((rel_x, rel_y))
