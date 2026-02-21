from typing import Dict, List, Optional
from uuid import UUID
import random
from .entities.base import Entity

class WorldState:
    """Contenedor global de un mundo extenso y procedimental."""
    def __init__(self):
        self.entities: Dict[UUID, Entity] = {}
        self.tick_count: int = 0
        self.decorations: Dict[tuple, str] = {}
        self._generate_world_procedural(radius=150)

    def _generate_world_procedural(self, radius: int):
        """Genera un mundo de 300x300 celdas con decoraciones variadas."""
        for _ in range(500):
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            # Evitar el centro (donde está el hogar)
            if abs(x) < 5 and abs(y) < 5: continue
            
            char = random.choice(["♣", "♣", "▲", "✿", "▒", "."])
            self.decorations[(x, y)] = char

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: UUID):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get_all_entities(self) -> List[Entity]:
        return list(self.entities.values())

    def update_all(self, delta_time: float):
        for entity in self.entities.values():
            entity.update(delta_time)
