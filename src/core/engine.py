import time
import math
from typing import Callable, List, Optional
from .state import WorldState
from .event_manager import EventManager
from .entities.person import Person
from .entities.wolf import Wolf
from .entities.town import Town
from .entities.shop import Shop
from .logger import logger

from .event_registry import EventRegistry

class SimulationEngine:
    def __init__(self, world_state: WorldState, fps: int = 15):
        self.world_state = world_state
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.is_running = False
        self.render_callbacks: List[Callable[[WorldState], None]] = []
        self.event_manager = EventManager(world_state)
        self.event_registry = EventRegistry() # NUEVO: Registro de eventos masivos
        
        self.last_logic_tick = 0
        self.logic_interval = 0.5 # TURBO: Decisiones cada medio segundo

    def register_render_callback(self, callback: Callable[[WorldState], None]):
        self.render_callbacks.append(callback)

    def _notify_renderers(self):
        for callback in self.render_callbacks:
            try:
                callback(self.world_state)
            except Exception as e:
                logger.log(f"RENDER ERROR: {str(e)}")

    def _handle_world_interactions(self):
        """Gestiona interacciones entre entidades (Peligros, Social, Town)."""
        entities = self.world_state.get_all_entities()
        people = [e for e in entities if isinstance(e, Person)]
        wolves = [e for e in entities if isinstance(e, Wolf)]
        towns = self.world_state.towns
        shops = [e for e in entities if isinstance(e, Shop)]

        # 1. PERSONAS vs LOBOS (Pánico)
        for p in people:
            # Proteccion: si está en un camino con vallas cercanas, el lobo no le ve
            is_protected = False
            px, py = int(p.x), int(p.y)
            if (px, py) in self.world_state.built_structures:
                # Comprobamos si hay vallas adyacentes (perímetro de seguridad)
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    if self.world_state.built_structures.get((px+dx, py+dy), {}).get("type") == "FENCE":
                        is_protected = True; break
            
            if not is_protected:
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

        # 3. PERSONAS vs SHOP (Compras)
        for p in people:
            for s in shops:
                dist = math.sqrt((p.x - s.x)**2 + (p.y - s.y)**2)
                if dist < 2.0:
                    s.interact(p)

        # 4. PERSONAS vs TOWN (Entrega de recursos)
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
                loop_start = time.time()
                dt = loop_start - start_time
                start_time = loop_start

                # Limitar dt para evitar saltos locos tras bloqueos
                dt = min(dt, 0.1)

                # 1. Movimiento (Física) y Tiempo Global
                self.world_state.update_time(dt) 
                is_night = self.world_state.is_night()
                scenario = self.world_state.scenario # Obtenemos el escenario
                
                entities = self.world_state.get_all_entities()
                for entity in entities:
                    try:
                        if isinstance(entity, Person):
                            biome = self.world_state.get_biome_at(entity.x, entity.y)
                            entity.update(dt, biome, scenario, self.world_state) # Pasamos world_state
                        elif isinstance(entity, Wolf):
                            entity.update(dt, is_night, self.world_state)
                        else:
                            entity.update(dt)
                    except Exception as e:
                        logger.log(f"ENTITY ERROR ({entity.name}): {str(e)}")

                # 2. Lógica y Eventos
                if loop_start - self.last_logic_tick > self.logic_interval:
                    try:
                        self._handle_world_interactions()
                        self.event_manager.update()
                        
                        # NUEVO: Disparar eventos contextuales
                        people = [e for e in entities if isinstance(e, Person)]
                        for p in people:
                            events = self.event_registry.get_random_event(p, self.world_state) # Pasamos self.world_state
                            for ev in events:
                                self.event_registry.apply_event(p, ev)
                    except Exception as e:
                        logger.log(f"LOGIC ERROR: {str(e)}")

                    self.world_state.tick_count += 1
                    self.last_logic_tick = loop_start

                # 3. Render
                self._notify_renderers()
                
                # Sleep dinámico pero seguro
                elapsed = time.time() - loop_start
                sleep_time = max(0.005, self.frame_time - elapsed)
                time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            # Guardar el error antes de salir
            with open("crash_log.txt", "w") as f:
                import traceback
                f.write(traceback.format_exc())
            self.stop()

    def stop(self):
        self.is_running = False
