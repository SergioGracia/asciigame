import random
from typing import Dict, Tuple, Any
from .base import BaseScenario

class NatureScenario(BaseScenario):
    name = "Nature"
    
    biomes_def = {
        "FOREST": {"char": "'", "solid": False, "speed_mult": 1.0, "stress_mod": 0, "energy_mod": 0, "pair_id": 11},
        "SWAMP": {"char": "=", "solid": False, "speed_mult": 0.5, "stress_mod": 1, "energy_mod": 0, "pair_id": 12},
        "DESERT": {"char": "~", "solid": False, "speed_mult": 1.3, "stress_mod": 0, "energy_mod": 1, "pair_id": 13},
        "MEADOW": {"char": ".", "solid": False, "speed_mult": 1.0, "stress_mod": -1, "energy_mod": 0, "pair_id": 10}
    }
    
    legend_def = [
        ("H", "Hogar", 2), ("J/M", "Ciudadanos", 1), ("W", "Lobo", 3),
        ("", "--- MUNDO ---", 5),
        ("T/'", "BOSQUE: Normal", 11), ("S/=", "PANTANO: Lento", 12),
        ("^/~", "DESIERTO: Calor", 13), ("f/.", "PRADERA: Relax", 10)
    ]

    def get_biome_id(self, x: float, y: float) -> str:
        if y > 40: return "FOREST"
        if y < -40: return "SWAMP"
        if x > 40: return "DESERT"
        return "MEADOW"

    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]:
        decorations = {}
        for _ in range(1200):
            x, y = random.randint(-radius, radius), random.randint(-radius, radius)
            if abs(x) < 5 and abs(y) < 5: continue
            biome = self.get_biome_id(x, y)
            if biome == "FOREST": char = "T"
            elif biome == "SWAMP": char = "S"
            elif biome == "DESERT": char = "^"
            else: char = "f"
            decorations[(x, y)] = char
        return decorations

    def is_walkable(self, x: float, y: float) -> bool:
        # En la naturaleza, casi todo es transitable (menos agua profunda, que simularemos con decoraciones)
        return True
