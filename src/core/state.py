from typing import Dict, List, Optional, Tuple
from uuid import UUID
import random
from .entities.base import Entity
from .scenarios.base import BaseScenario

class WorldState:
    """Mundo cuyo comportamiento depende del escenario activo."""
    def __init__(self, scenario: BaseScenario):
        self.scenario = scenario
        self.entities: Dict[UUID, Entity] = {}
        self.tick_count: int = 0
        self.time_of_day = 12.0
        # El escenario genera el mapa
        self.decorations = self.scenario.generate_decorations(radius=150)

    def get_biome_at(self, x: float, y: float) -> str:
        return self.scenario.get_biome_id(x, y)

    def get_ground_char(self, x: int, y: int) -> str:
        biome_id = self.get_biome_at(x, y)
        return self.scenario.get_ground_char(biome_id)

    def get_biome_stats(self, x: float, y: float) -> dict:
        biome_id = self.get_biome_at(x, y)
        return self.scenario.get_biome_stats(biome_id)

    def update_time(self, dt: float):
        self.time_of_day += (dt * 0.1)
        if self.time_of_day >= 24.0: self.time_of_day = 0.0

    def is_night(self) -> bool:
        return self.time_of_day > 20.0 or self.time_of_day < 6.0

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def get_all_entities(self) -> List[Entity]:
        return list(self.entities.values())

    def update_all(self, delta_time: float):
        self.update_time(delta_time)
        for entity in self.entities.values():
            entity.update(delta_time)
