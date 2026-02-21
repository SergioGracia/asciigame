import random
import math
from .base import Entity
from ..logger import logger
from .town import Town

class Person(Entity):
    def __init__(self, name: str, x: float = 0.0, y: float = 0.0, goal: str = "BUILDER"):
        super().__init__(name, x, y)
        self.energy = 100
        self.inventory = {"wood": 0}
        self.state = "IDLE" 
        self.wealth = random.randint(5, 20)
        self.stress = 0
        self.goal = goal
        self.target_x, self.target_y = x, y
        self.base_speed = 6.0 if goal == "TRADER" else 5.0
        self.speed = self.base_speed
        self.action_timer = 0.0
        self.social_cooldown = 0.0
        self.current_biome = "MEADOW"

    def move_towards(self, tx, ty):
        self.target_x, self.target_y = tx, ty

    def update(self, dt: float, biome: str = "MEADOW", scenario=None):
        self.current_biome = biome
        
        # 1. AJUSTES FISICOS SEGUN BIOMA
        if biome == "INTERIOR":
            self.energy += 1.0 * dt
            self.stress -= 2.0 * dt
            self.speed = self.base_speed * 0.5
        elif biome == "STREET" or biome == "DESERT":
            self.speed = self.base_speed * 1.5
            self.stress += 0.5 * dt
        elif biome == "SWAMP":
            self.speed = self.base_speed * 0.5
            self.stress += 0.2 * dt
        else:
            self.speed = self.base_speed

        # 2. MOVIMIENTO CON COLISIONES
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.1:
            move_speed = self.speed * 2.0 if self.state == "PANICKING" else self.speed
            step = move_speed * dt
            if step > dist: step = dist
            
            nx, ny = self.x + (dx / dist) * step, self.y + (dy / dist) * step
            
            if scenario and scenario.is_walkable(nx, ny):
                self.x, self.y = nx, ny
            else:
                # Si choca, rebote y nueva meta al azar
                self.target_x = self.x + random.uniform(-20, 20)
                self.target_y = self.y + random.uniform(-20, 20)
        
        # 3. LÓGICA DE IA
        self.action_timer += dt
        if self.social_cooldown > 0: self.social_cooldown -= dt
        if self.action_timer > 2.5:
            self.action_timer = 0
            self._logic_tick()

    def _logic_tick(self):
        # Fatiga natural
        if self.current_biome != "INTERIOR":
            self.energy -= 1
            if self.stress > 50: self.energy -= 1

        # CRISIS DE ESTRÉS
        if self.stress >= 85 and self.state != "STRIKE":
            self.state = "STRIKE"
            logger.log(f"CRISIS: {self.name} ha colapsado por estres.")
            self.move_towards(self.x + random.uniform(-10, 10), self.y + random.uniform(-10, 10))

        if self.state == "STRIKE":
            if self.stress < 40:
                self.state = "IDLE"
                logger.log(f"GOOD: {self.name} se siente mejor.")
            return

        # IA NORMAL
        if self.current_biome == "INTERIOR":
            if self.energy >= 100:
                # Buscar salida (asumimos puerta cerca del origen en modo Nature o 24,35 en Urban)
                self.state = "IDLE"
                self.move_towards(self.x, self.y + 10)
                logger.log(f"{self.name} sale a trabajar.")
            return

        if self.energy < 25 or self.state == "GOING_HOME":
            # Meta: Puerta de la base (simplificado para ser robusto)
            # En Nature es 0,0. En Urban es 24,35.
            target_x, target_y = (24, 35) if self.speed > 6.0 else (0, 0) # Heuristic
            self.state = "GOING_HOME"
            self.move_towards(target_x, target_y)
            if random.random() < 0.1: logger.log(f"{self.name} vuelve a la base.")

        elif self.state == "IDLE":
            if random.random() < 0.3:
                self.state = "SEARCHING"
                self.move_towards(random.randint(-100, 100), random.randint(-100, 100))
                logger.log(f"{self.name} explorando el mundo.")

        elif self.state == "SEARCHING":
            if random.random() < 0.1:
                self.inventory["wood"] += 1
                if self.inventory["wood"] >= (6 if self.goal == "BUILDER" else 3):
                    self.state = "GOING_HOME"
                    logger.log(f"{self.name} cargado de recursos, vuelve a casa.")

    def react_to_danger(self, dx, dy):
        if self.current_biome != "INTERIOR":
            self.state = "PANICKING"
            self.stress += 20
            logger.log(f"ALARM: {self.name} huye de un peligro!")
            self.move_towards(self.x + (self.x-dx)*10, self.y + (self.y-dy)*10)

    def social_interaction(self, other):
        if self.social_cooldown <= 0:
            self.social_cooldown = 30.0
            self.stress = max(0, self.stress - 15)
            logger.log(f"TALK: {self.name} y {other.name} charlan.")
