import random
import math
from typing import Dict, Tuple, Any, List
from .base import BaseScenario

class UrbanScenario(BaseScenario):
    name = "Urban"
    
    biomes_def = {
        "STREET": {"char": "#", "solid": False, "speed_mult": 1.8, "stress_mod": 1, "pair_id": 14},
        "SIDEWALK": {"char": ".", "solid": False, "speed_mult": 1.0, "stress_mod": 0, "pair_id": 15},
        "WALL": {"char": "X", "solid": True, "speed_mult": 0, "stress_mod": 0, "pair_id": 5},
        "INTERIOR": {"char": " ", "solid": False, "speed_mult": 0.6, "stress_mod": -2, "pair_id": 16},
        "PARK": {"char": "v", "solid": False, "speed_mult": 1.0, "stress_mod": -3, "pair_id": 17},
        "CONSTRUCTION": {"char": "!", "solid": True, "speed_mult": 0, "stress_mod": 0, "pair_id": 13} # Amarillo
    }
    
    legend_def = [
        ("X", "MURO", 5), ("+", "PUERTA", 4), ("!", "OBRAS", 13),
        ("#", "CALLE", 14), (".", "ACERA", 15), ("v", "PARQUE", 17)
    ]

    def get_biome_id(self, x: float, y: float) -> str:
        # Distritos: Centro (Comercial), Periferia (Parques), Zonas Industriales
        dist = math.sqrt(x**2 + y**2)
        
        # 1. Parques Metropolitanos en la periferia
        if dist > 120: return "PARK"
        
        # 2. Rejilla de manzanas (Blocks)
        bx, by = int(x) % 50, int(y) % 50
        
        # Calles más anchas en avenidas principales
        street_width = 10 if (int(x)//50) % 3 == 0 else 6
        
        if bx < street_width or by < street_width:
            return "STREET"
        if bx < street_width + 2 or bx >= 48 or by < street_width + 2 or by >= 48:
            return "SIDEWALK"
            
        # 3. Zonas en Construcción aleatorias
        if (int(x)//50 + int(y)//50) % 7 == 0:
            if bx > 20 and by > 20 and bx < 30 and by < 30:
                return "CONSTRUCTION"

        # 4. Edificios
        if bx == street_width + 2 or bx == 47 or by == street_width + 2 or by == 47:
            return "WALL"
            
        return "INTERIOR"

    def is_door(self, x: int, y: int) -> bool:
        bx, by = x % 50, y % 50
        # Puerta en el centro de la fachada
        if by == 47 and bx == 25: return True
        return False

    def get_home_coords(self) -> Tuple[int, int]:
        return (24, 24) # Centro del edificio inicial en la manzana 40x40

    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]:
        decorations = {}
        for x in range(-radius, radius, 50):
            for y in range(-radius, radius, 50):
                decorations[(x + 25, y + 47)] = "+" # Puertas
                if random.random() < 0.3:
                    decorations[(x + 10, y + 10)] = "o" # Papeleras
        return decorations
