import time
from typing import Callable, List, Optional
from .state import WorldState
from .event_manager import EventManager

class SimulationEngine:
    def __init__(self, world_state: WorldState, fps: int = 20):
        self.world_state = world_state
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.is_running = False
        self.render_callbacks: List[Callable[[WorldState], None]] = []
        self.event_manager = EventManager(world_state)
        
        # Control de tiempo para la lógica (independiente del render)
        self.last_logic_tick = 0
        self.logic_interval = 2.0 # Segundos entre ticks lógicos (Antes 0.5)

    def register_render_callback(self, callback: Callable[[WorldState], None]):
        self.render_callbacks.append(callback)

    def _notify_renderers(self):
        for callback in self.render_callbacks:
            callback(self.world_state)

    def run(self):
        self.is_running = True
        start_time = time.time()
        
        try:
            while self.is_running:
                current_time = time.time()
                dt = current_time - start_time
                start_time = current_time

                # 1. LÓGICA DE MOVIMIENTO (Cada frame para fluidez)
                # Las entidades se mueven un poco en cada frame según su velocidad
                for entity in self.world_state.get_all_entities():
                    entity.update(dt)

                # 2. LÓGICA DE DECISIÓN (IA y Eventos - Más lenta)
                if current_time - self.last_logic_tick > self.logic_interval:
                    self.event_manager.update()
                    self.world_state.tick_count += 1
                    self.last_logic_tick = current_time

                # 3. RENDERIZADO (A máxima velocidad de FPS)
                self._notify_renderers()
                
                # Dormir para mantener los FPS
                sleep_time = self.frame_time - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False
