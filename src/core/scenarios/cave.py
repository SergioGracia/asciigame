import random
import math
from typing import Dict, Tuple, Any
from .base import BaseScenario

class CaveScenario(BaseScenario):
    name = "Submundo"
    
    biomes_def = {
        "WALL": {"char": "#", "solid": True, "pair_id": 5},
        "FLOOR": {"char": ".", "solid": False, "pair_id": 5},
        "CRYSTAL": {"char": "*", "solid": False, "pair_id": 1}, # Cian
        "LAVA": {"char": "~", "solid": True, "pair_id": 3},   # Rojo
        "WATER": {"char": "~", "solid": True, "pair_id": 12},  # Azul
        "GOLD_VEIN": {"char": "$", "solid": True, "pair_id": 2} # Amarillo
    }
    
    def __init__(self, seed: int = None, level: int = 1):
        self.seed = seed or random.randint(0, 1000000)
        self.level = level
        self.rng = random.Random(self.seed)

    def _hash(self, x: int, y: int) -> float:
        n = (x * 15731 + y * 789221 + self.seed + self.level) & 0x7fffffff
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    def _noise(self, x: float, y: float) -> float:
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        v00 = self._hash(ix, iy)
        v10 = self._hash(ix + 1, iy)
        v01 = self._hash(ix, iy + 1)
        v11 = self._hash(ix + 1, iy + 1)
        t = fx * fx * (3 - 2 * fx) # Smoothstep simplificado
        u = fy * fy * (3 - 2 * fy)
        return v00 + t*(v10-v00) + u*(v01-v00) + t*u*(v00-v10-v01+v11)

    def get_biome_id(self, x: float, y: float) -> str:
        # Ruido base para túneles
        n = self._noise(x * 0.1, y * 0.1)
        
        # Umbral para pasillos (Túneles orgánicos)
        if abs(n) < 0.25:
            # Dentro del túnel, ver si hay lava o cristales
            detail = self._noise(x * 0.5, y * 0.5)
            if detail > 0.8: return "LAVA"
            if detail < -0.8: return "CRYSTAL"
            return "FLOOR"
        
        # Muros y vetas de oro
        if abs(n) > 0.85: return "GOLD_VEIN"
        return "WALL"

    def get_ground_char(self, x: int, y: int, biome_id: str) -> str:
        # Entrada/Salida siempre libre en el origen local (para no aparecer en un muro)
        if abs(x) < 2 and abs(y) < 2: return "0" # Portal de retorno
        return self.biomes_def[biome_id]["char"]

    def is_walkable(self, x: float, y: float) -> bool:
        return not self.biomes_def[self.get_biome_id(x, y)]["solid"]

    def get_biome_stats(self, biome_id: str) -> Dict[str, Any]:
        return self.biomes_def.get(biome_id, {})
