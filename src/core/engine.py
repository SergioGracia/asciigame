import time
import math
from typing import Callable, List, Optional
from .state import WorldState
from .event_manager import EventManager
from .entities.person import Person
from .entities.wolf import Wolf
from .entities.town import Town
from .logger import logger

class SimulationEngine:
    def __init__(self, world_state: WorldState, fps: int = 20):
        self.world_state = world_state
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.is_running = False
        self.render_callbacks: List[Callable[[WorldState], None]] = []
        self.event_manager = EventManager(world_state)
        
        self.last_logic_tick = 0
        self.logic_interval = 2.0 

    def register_render_callback(self, callback: Callable[[WorldState], None]):
        self.render_callbacks.append(callback)

    def _notify_renderers(self):
        for callback in self.render_callbacks:
            callback(self.world_state)

    def _handle_world_interactions(self):
        """Gestiona interacciones entre entidades (Peligros, Social, Town)."""
        entities = self.world_state.get_all_entities()
        people = [e for e in entities if isinstance(e, Person)]
        wolves = [e for e in entities if isinstance(e, Wolf)]
        towns = [e for e in entities if isinstance(e, Town)]

        # 1. PERSONAS vs LOBOS (Pánico)
        for p in people:
            for w in wolves:
                dist = math.sqrt((p.x - w.x)**2 + (p.y - w.y)**2)
                if dist < 5.0:
                    p.react_to_danger(w.x, w.y)

        # 2. PERSONAS vs PERSONAS (Social)
        for i, p1 in enumerate(people):
            for p2 in people[i+1:]:
                dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                if dist < 1.8:
                    p1.social_interaction(p2)
                    p2.social_interaction(p1)

        # 3. PERSONAS vs TOWN (Entrega de recursos)
        for p in people:
            for t in towns:
                dist = math.sqrt((p.x - t.x)**2 + (p.y - t.y)**2)
                if dist < 1.0 and p.inventory["wood"] > 0:
                    logger.log(f"BUILD: {p.name} entrego {p.inventory['wood']} de recursos a {t.name}.")
                    t.add_wood(p.inventory["wood"])
                    p.inventory["wood"] = 0
                    p.state = "RESTING" 

    def run(self):
        self.is_running = True
        start_time = time.time()
        
        try:
            while self.is_running:
                current_time = time.time()
                dt = current_time - start_time
                start_time = current_time

                # 1. Movimiento (Física) y Tiempo Global
                self.world_state.update_time(dt) 
                is_night = self.world_state.is_night()
                scenario = self.world_state.scenario # Obtenemos el escenario
                
                for entity in self.world_state.get_all_entities():
                    if isinstance(entity, Person):
                        biome = self.world_state.get_biome_at(entity.x, entity.y)
                        entity.update(dt, biome, scenario)
                    elif isinstance(entity, Wolf):
                        entity.update(dt, is_night, scenario)
                    else:
                        entity.update(dt)

                # 2. Lógica y Eventos
                if current_time - self.last_logic_tick > self.logic_interval:
                    self._handle_world_interactions()
                    self.event_manager.update()
                    self.world_state.tick_count += 1
                    self.last_logic_tick = current_time

                # 3. Render
                self._notify_renderers()
                
                sleep_time = self.frame_time - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False
