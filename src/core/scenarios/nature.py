import random
import math
from typing import Dict, Tuple, Any
from .base import BaseScenario

class NatureScenario(BaseScenario):
    name = "Nature"
    
    biomes_def = {
        "SNOW_PEAK": {"char": "A", "solid": True, "pair_id": 5},
        "MOUNTAIN": {"char": "^", "solid": True, "pair_id": 5},
        "HILLS": {"char": "n", "solid": False, "pair_id": 11},
        "FOREST": {"char": "'", "solid": False, "pair_id": 11},
        "MEADOW": {"char": ".", "solid": False, "pair_id": 10},
        "BEACH": {"char": "p", "solid": False, "pair_id": 13}, 
        "SWAMP": {"char": "=", "solid": False, "pair_id": 12},
        "WATER": {"char": "~", "solid": True, "pair_id": 12},
        "RIVER": {"char": "s", "solid": True, "pair_id": 12},
        "DEEP_OCEAN": {"char": " ", "solid": True, "pair_id": 12},
        "ABYSS": {"char": "_", "solid": True, "pair_id": 5},
        "DESERT": {"char": "-", "solid": False, "pair_id": 13},
        "TUNDRA": {"char": "*", "solid": False, "pair_id": 5},
        "GLACIER": {"char": "X", "solid": True, "pair_id": 5}
    }
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        self.rng = random.Random(self.seed)

    def _hash(self, x: int, y: int) -> float:
        n = (x * 15731 + y * 789221 + self.seed) & 0x7fffffff
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    def _lerp(self, a, b, t): return a + t * (b - a)
    def _fade(self, t): return t * t * t * (t * (t * 6 - 15) + 10)

    def _noise(self, x: float, y: float) -> float:
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        v00 = self._hash(ix, iy)
        v10 = self._hash(ix + 1, iy)
        v01 = self._hash(ix, iy + 1)
        v11 = self._hash(ix + 1, iy + 1)
        ux, uy = self._fade(fx), self._fade(fy)
        return self._lerp(self._lerp(v00, v10, ux), self._lerp(v01, v11, ux), uy)

    def _octave_noise(self, x: float, y: float, octaves: int = 5, freq: float = 0.01) -> float:
        val, amp, max_amp, f = 0.0, 1.0, 0.0, freq
        for _ in range(octaves):
            val += self._noise(x * f, y * f) * amp
            max_amp += amp
            f *= 2.0; amp *= 0.5
        return val / max_amp

    def get_biome_id(self, x: float, y: float) -> str:
        elev = self._octave_noise(x, y, octaves=5, freq=0.008)
        
        # RÍOS (Ridged Noise)
        river_noise = abs(self._octave_noise(x + 311, y + 91, octaves=2, freq=0.02))
        is_river = river_noise < 0.04 and elev > -0.15

        hum = self._octave_noise(x + 523, y + 117, octaves=3, freq=0.015)
        temp_distort = self._noise(x * 0.005, y * 0.005) * 200
        temp = (1.0 - abs(y + temp_distort) / 4000.0) - (elev * 0.4)
        
        if is_river and elev < 0.5: return "RIVER"

        if elev < -0.8: return "ABYSS"
        if elev < -0.5: return "DEEP_OCEAN"
        if elev < -0.15: return "WATER"
        if -0.15 <= elev < -0.05: return "BEACH"
        
        if elev > 0.8: return "SNOW_PEAK"
        if elev > 0.6: return "MOUNTAIN"
        if elev > 0.35: return "HILLS"
        
        if temp < -0.1: return "GLACIER"
        if temp < 0.2: return "TUNDRA"
        
        if temp > 0.6:
            if hum < -0.4: return "DESERT"
            if hum > 0.4: return "SWAMP"
            return "MEADOW"
            
        if hum > 0.2: return "FOREST"
        return "MEADOW"

    def get_ground_char(self, x: int, y: int, biome_id: str) -> str:
        # 1. ¿HAY UNA ESTRUCTURA AQUÍ? (Ruinas o Cuevas)
        # Usamos un hash de celda grande (ej. cada 100x100 unidades)
        gx, gy = x // 60, y // 60
        struct_seed = self._hash(gx, gy)
        
        # Si el hash es alto, hay una ruina o cueva en el centro de esta celda
        if struct_seed > 0.95:
            cx, cy = gx * 60 + 30, gy * 60 + 30
            dx, dy = x - cx, y - cy
            
            # Patrón de RUINA (Un pequeño templo derruido 5x5)
            if struct_seed > 0.97:
                if abs(dx) <= 2 and abs(dy) <= 2:
                    if abs(dx) == 2 or abs(dy) == 2: return "#" # Muros
                    if dx == 0 and dy == 0: return "X" # Altar
                    return "." # Suelo interior
            
            # Patrón de CUEVA (Solo en montañas/colinas)
            elif biome_id in ["MOUNTAIN", "HILLS", "SNOW_PEAK"]:
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return "0" if dx == 0 and dy == 0 else "n"

        return self.biomes_def.get(biome_id, {}).get("char", ".")

    def get_ground_attr(self, x: int, y: int, char: str) -> int:
        # Colores especiales para estructuras
        if char in ["#", "X"]: return 5 # Blanco/Gris
        if char == "0": return 3 # Rojo/Oscuro para cuevas
        return 0 # Default

    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]:
        decorations = {}
        for _ in range(800):
            x = self.rng.randint(-radius, radius)
            y = self.rng.randint(-radius, radius)
            biome = self.get_biome_id(x, y)
            if biome == "FOREST": decorations[(x, y)] = "T"
            elif biome == "MEADOW" and self.rng.random() < 0.2: decorations[(x, y)] = "f"
            elif biome == "DESERT" and self.rng.random() < 0.05: decorations[(x, y)] = "C"
        return decorations
