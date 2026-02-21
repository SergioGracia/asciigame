import random
from typing import Dict, Tuple, Any, List
from .base import BaseScenario

class UrbanScenario(BaseScenario):
    name = "Urban"
    
    # Definición de biomas con magnitudes reales
    biomes_def = {
        "STREET": {"char": "#", "solid": False, "speed_mult": 1.8, "stress_mod": 1, "pair_id": 14},
        "SIDEWALK": {"char": ".", "solid": False, "speed_mult": 1.0, "stress_mod": 0, "pair_id": 15},
        "WALL": {"char": "X", "solid": True, "speed_mult": 0, "stress_mod": 0, "pair_id": 5},
        "INTERIOR": {"char": " ", "solid": False, "speed_mult": 0.6, "stress_mod": -2, "pair_id": 16},
        "PARK": {"char": "v", "solid": False, "speed_mult": 1.0, "stress_mod": -3, "pair_id": 17}
    }
    
    legend_def = [
        ("X", "MURO DE EDIFICIO", 5), ("+", "PUERTA DE ACCESO", 4),
        ("#", "CALZADA (Coches)", 14), (".", "ACERA (Peatones)", 15),
        (" ", "INTERIOR (Oficinas)", 16), ("v", "PARQUE", 17)
    ]

    def get_biome_id(self, x: float, y: float) -> str:
        # Rejilla de 40 unidades para una manzana real
        bx, by = int(x) % 40, int(y) % 40
        
        # 1. Calles (Asfalto) - 8 unidades de ancho
        if bx < 8 or by < 8:
            return "STREET"
            
        # 2. Aceras - 2 unidades a cada lado de la calle
        if bx < 10 or bx >= 38 or by < 10 or by >= 38:
            return "SIDEWALK"
            
        # 3. Manzana de Edificios (10 a 38)
        # Dejamos 2 unidades de "pavement" antes del muro
        if bx < 12 or bx >= 36 or by < 12 or by >= 36:
            return "SIDEWALK"
            
        # 4. El Edificio (12 a 36)
        # Muros
        if bx == 12 or bx == 35 or by == 12 or by == 35:
            return "WALL"
            
        # Interior
        return "INTERIOR"

    def is_door(self, x: int, y: int) -> bool:
        """Puertas en el centro de la fachada sur de cada edificio (Y=35)."""
        bx, by = x % 40, y % 40
        # Puerta en el centro de la pared sur (by=35) de la manzana
        if by == 35 and bx == 24:
            return True
        return False

    def is_walkable(self, x: float, y: float) -> bool:
        bx, by = int(x), int(y)
        if self.is_door(bx, by): return True
        biome = self.get_biome_id(x, y)
        return not self.biomes_def[biome].get("solid", False)

    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]:
        decorations = {}
        # Decoraciones básicas: Puertas y algún detalle en aceras
        for x in range(-radius, radius, 40):
            for y in range(-radius, radius, 40):
                # Puerta sur del edificio de esta manzana
                decorations[(x + 24, y + 35)] = "+"
        return decorations
