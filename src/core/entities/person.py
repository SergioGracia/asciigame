import random
import math
from .base import Entity
from ..logger import logger
from .town import Town
from .shop import Shop
from ..pathfinding import Pathfinder

class Person(Entity):
    def __init__(self, name: str, x: float = 0.0, y: float = 0.0, goal: str = "BUILDER", traits: list = None):
        super().__init__(name, x, y)
        self.energy = 100
        self.wealth = random.randint(20, 50)
        self.stress = 0
        self.name = name
        self.goal = goal
        self.traits = traits if traits else []
        self.state = "IDLE" 
        self.inventory = {"wood": 0, "food": 0, "medkit": 0}
        self.base_speed = 8.0 # Velocidad controlada
        self.speed = self.base_speed
        self.target_x, self.target_y = x, y
        self.path = []
        self.pathfinder = None
        self.action_timer = 0.0
        self.social_cooldown = 0.0
        self.path_retry_timer = 0.0 # NUEVO: Tiempo para reintentar ruta
        self.current_biome = "MEADOW"
        self.home_reference = None
        self.last_road_pos = (None, None)
        self.is_constructing = False 

    def move_towards(self, tx, ty):
        if (self.target_x, self.target_y) != (tx, ty):
            self.target_x, self.target_y = tx, ty
            self.path = []
            self.path_retry_timer = 0.0

    def update(self, dt: float, biome: str = "MEADOW", scenario=None, world_state=None):
        self.current_biome = biome
        
        # 1. SEGURIDAD: Si está en terreno prohibido, rescatarlo
        if world_state and not world_state.is_walkable(self.x, self.y):
            self.x, self.y = 0.0, 0.0 # Rescate a base
            self.path = []

        # 2. METABOLISMO
        if self.state == "RESTING" or biome == "INTERIOR":
            self.energy = min(100.0, self.energy + 15.0 * dt)
            self.stress = max(0.0, self.stress - 10.0 * dt)
            self.speed = self.base_speed * 0.5
        else:
            self.energy = max(0.0, self.energy - 0.5 * dt)
            speed_mod = 2.0 if world_state and (int(self.x), int(self.y)) in world_state.built_structures else 1.0
            self.speed = self.base_speed * speed_mod

        # 3. MOVIMIENTO ORTOGONAL ESTRICTO
        if world_state:
            if self.path_retry_timer > 0:
                self.path_retry_timer -= dt
            self._follow_path_orthogonal(dt, world_state)
        
        # 4. LÓGICA DE IA
        self.action_timer += dt
        if self.action_timer > 1.0: # Ritmo razonable
            self.action_timer = 0
            self._logic_tick(world_state)

    def _follow_path_orthogonal(self, dt, world_state):
        if not self.path:
            if self.path_retry_timer > 0: return # Enfriamiento activo
            
            if not self.pathfinder: self.pathfinder = Pathfinder(world_state)
            self.path = self.pathfinder.get_path((self.x, self.y), (self.target_x, self.target_y))
            
            if not self.path:
                self.path_retry_timer = 2.0 # Si falla, esperar 2 segundos
                return

        target_node = self.path[0]
        dx = target_node[0] - self.x
        dy = target_node[1] - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 0.2:
            self.path.pop(0)
            return

        move_step = self.speed * dt
        # FORZAR MOVIMIENTO POR EJES (Garantiza caminos rectos)
        if abs(dx) > 0.01:
            step = math.copysign(min(move_step, abs(dx)), dx)
            if world_state.is_walkable(self.x + step, self.y):
                self.x += step
                self._build_road_step(world_state)
            else: self.path = [] # Re-ruta
        elif abs(dy) > 0.01:
            step = math.copysign(min(move_step, abs(dy)), dy)
            if world_state.is_walkable(self.x, self.y + step):
                self.y += step
                self._build_road_step(world_state)
            else: self.path = []

    def _build_road_step(self, world_state):
        """Pone una celda de camino si tiene madera y va a casa."""
        bx, by = int(self.x), int(self.y)
        if self.state == "GOING_HOME" and self.inventory["wood"] > 0:
            if (bx, by) != self.last_road_pos and (bx, by) not in world_state.built_structures:
                if self.current_biome not in ["INTERIOR", "OFFICE"]:
                    world_state.add_structure(bx, by, "ROAD")
                    self.inventory["wood"] -= 0.1
                    self.last_road_pos = (bx, by)

    def _logic_tick(self, world_state=None):
        if self.state == "RESTING":
            if self.energy >= 100: self.state = "IDLE"
            return

        if not self.home_reference:
            for e in world_state.get_all_entities():
                if isinstance(e, Town) and (e.owner_name == self.name or self.name in e.residents):
                    self.home_reference = e; break

        # REGRESAR
        if self.energy < 40 or self.inventory["wood"] >= 10:
            hx, hy = (self.home_reference.x, self.home_reference.y) if self.home_reference else (0, 0)
            if math.sqrt((self.x-hx)**2 + (self.y-hy)**2) < 2.5:
                if self.inventory["wood"] > 0 and self.home_reference:
                    self.home_reference.add_wood(int(self.inventory["wood"]))
                    self.inventory["wood"] = 0
                self.state = "RESTING"; self.move_towards(hx, hy)
            else:
                self.state = "GOING_HOME"; self.move_towards(hx, hy)
            return

        if self.state == "IDLE":
            self.state = "SEARCHING"
            self.move_towards(random.randint(-100, 100), random.randint(-100, 100))
        elif self.state == "SEARCHING":
            if random.random() < 0.2 and self.current_biome in ["FOREST", "OFFICE"]:
                self.state = "GATHERING"
        elif self.state == "GATHERING":
            self.inventory["wood"] += 2

    def react_to_danger(self, dx, dy):
        if "BRAVE" in self.traits: return
        self.state = "PANICKING"
        logger.log(f"ALARM: ¡{self.name} huye de un peligro!")
        self.move_towards(self.x + (self.x-dx)*10, self.y + (self.y-dy)*10)

    def social_interaction(self, other):
        if self.social_cooldown <= 0:
            self.social_cooldown = 20.0
            logger.log(f"TALK: {self.name} y {other.name} charlan.")
