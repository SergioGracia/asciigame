from typing import Dict, List, Optional, Tuple
from uuid import UUID
import random
from .entities.base import Entity
from .scenarios.base import BaseScenario
from .entities.town import Town

class WorldState:
    def __init__(self, scenario: BaseScenario):
        self.scenario = scenario
        self.entities: Dict[UUID, Entity] = {}
        self.towns: List[Town] = [] # CACHE DE EDIFICIOS
        self.tick_count: int = 0
        self.time_of_day = 12.0
        self.decorations = self.scenario.generate_decorations(radius=150)
        self.built_structures: Dict[Tuple[int, int], Dict] = {}

    def add_structure(self, x: int, y: int, struct_type: str):
        if struct_type == "BRIDGE":
            self.built_structures[(x, y)] = {"char": "=", "solid": False, "type": "BRIDGE"}
        elif struct_type == "ROAD":
            self.built_structures[(x, y)] = {"char": ":", "solid": False, "type": "ROAD"}
        elif struct_type == "FENCE":
            self.built_structures[(x, y)] = {"char": "#", "solid": True, "type": "FENCE"}

    def is_walkable(self, x: float, y: float) -> bool:
        bx, by = int(x), int(y)
        
        # 1. Comprobar si hay un edificio (Town) en esa posición (USANDO CACHE)
        for town in self.towns:
            tile = town.get_tile_at(bx, by)
            if tile: return not tile["solid"]

        # 2. Construcciones manuales
        if (bx, by) in self.built_structures:
            return not self.built_structures[(bx, by)]["solid"]
        
        # 3. Escenario base
        return self.scenario.is_walkable(x, y)

    def get_ground_char(self, x: int, y: int) -> str:
        # 1. Prioridad: Edificios complejos (Town)
        for town in self.towns:
            tile = town.get_tile_at(x, y)
            if tile: return tile["char"]

        # 2. Construcciones manuales
        if (x, y) in self.built_structures:
            return self.built_structures[(x, y)]["char"]
        
        # 3. Escenario base
        biome_id = self.scenario.get_biome_id(x, y)
        return self.scenario.get_ground_char(biome_id)

    def get_biome_at(self, x: float, y: float) -> str:
        # Si está dentro de un edificio, el bioma es INTERIOR para recuperar energía
        for town in self.towns:
            if town.is_inside(x, y):
                return "INTERIOR"
        return self.scenario.get_biome_id(x, y)

    def update_time(self, dt: float):
        self.time_of_day += (dt * 0.1)
        if self.time_of_day >= 24.0: self.time_of_day = 0.0

    def is_night(self) -> bool:
        return self.time_of_day > 20.0 or self.time_of_day < 6.0

    def add_entity(self, entity: Entity):
        # Evitar spawn en muros de Town
        if not self.is_walkable(entity.x, entity.y):
            entity.x += 2.0; entity.y += 2.0
            
        self.entities[entity.id] = entity
        if isinstance(entity, Town):
            self.towns.append(entity)

    def get_all_entities(self) -> List[Entity]:
        return list(self.entities.values())

    def update_all(self, delta_time: float):
        self.update_time(delta_time)
        for entity in self.entities.values():
            entity.update(delta_time)
