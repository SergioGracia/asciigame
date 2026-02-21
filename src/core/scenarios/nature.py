import random
import math
from typing import Dict, Tuple, Any
from .base import BaseScenario

class NatureScenario(BaseScenario):
    name = "Nature"
    
    biomes_def = {
        "MOUNTAIN": {"char": "^", "solid": True, "speed_mult": 0, "stress_mod": 0, "pair_id": 5},
        "FOREST": {"char": "'", "solid": False, "speed_mult": 0.8, "stress_mod": -1, "pair_id": 11},
        "MEADOW": {"char": ".", "solid": False, "speed_mult": 1.0, "stress_mod": -2, "pair_id": 10},
        "SWAMP": {"char": "=", "solid": False, "speed_mult": 0.4, "stress_mod": 2, "pair_id": 12},
        "WATER": {"char": "~", "solid": True, "speed_mult": 0, "stress_mod": 0, "pair_id": 12},
        "DESERT": {"char": "-", "solid": False, "speed_mult": 1.2, "stress_mod": 1, "pair_id": 13},
        "TUNDRA": {"char": "*", "solid": False, "speed_mult": 0.6, "stress_mod": 1, "pair_id": 5}
    }
    
    legend_def = [
        ("H", "Hogar", 2), ("J/M", "Ciudadanos", 1), ("W", "Lobo", 3),
        ("", "--- GEOGRAFIA ---", 5),
        ("^", "MONTAÑA (Impasable)", 5), ("~", "AGUA (Impasable)", 12),
        ("'", "BOSQUE", 11), ("=", "PANTANO", 12), (".", "PRADERA", 10),
        ("*", "TUNDRA", 5), ("-", "DESIERTO", 13)
    ]

    def _pseudo_noise(self, x: float, y: float) -> float:
        """Función de ruido determinista para biomas orgánicos."""
        val = math.sin(x * 0.05) + math.sin(y * 0.05) + math.sin((x + y) * 0.03)
        return val / 3.0

    def get_biome_id(self, x: float, y: float) -> str:
        noise = self._pseudo_noise(x, y)
        
        # Capa de altura/humedad simplificada
        if noise > 0.7: return "MOUNTAIN"
        if noise > 0.3: return "FOREST"
        if noise > -0.1: return "MEADOW"
        if noise > -0.4: return "SWAMP"
        if noise > -0.7: return "WATER"
        
        # Variación por distancia para Desierto/Tundra
        dist = math.sqrt(x**2 + y**2)
        if dist > 100: return "TUNDRA" if y > 0 else "DESERT"
        
        return "MEADOW"

    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]:
        decorations = {}
        # 1. Decoración de biomas
        for _ in range(1500):
            x, y = random.randint(-radius, radius), random.randint(-radius, radius)
            if abs(x) < 5 and abs(y) < 5: continue
            
            biome = self.get_biome_id(x, y)
            if biome == "FOREST": decorations[(x, y)] = "T"
            elif biome == "MEADOW": decorations[(x, y)] = "f" if random.random() < 0.1 else "v"
            elif biome == "MOUNTAIN": decorations[(x, y)] = "A"
            elif biome == "WATER": decorations[(x, y)] = "o" # Rocas en agua
            elif biome == "SWAMP": decorations[(x, y)] = "S"
            
        # 2. Estructuras Prefabricadas (Ruinas)
        for _ in range(5):
            rx, ry = random.randint(-radius, radius), random.randint(-radius, radius)
            # Dibujar una pequeña ruina de 3x3
            for dx in range(3):
                for dy in range(3):
                    if random.random() < 0.7:
                        decorations[(rx+dx, ry+dy)] = "r"
                        
        return decorations
