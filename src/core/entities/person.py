import random
import math
from .base import Entity
from ..logger import logger

class Person(Entity):
    def __init__(self, name: str, x: float = 0.0, y: float = 0.0):
        super().__init__(name, x, y)
        self.energy = 100
        self.inventory = {"wood": 0}
        self.state = "IDLE" # IDLE, SEARCHING, GATHERING, GOING_HOME, RESTING
        self.wealth = random.randint(5, 20)
        self.stress = 0
        
        self.target_x = x
        self.target_y = y
        self.speed = 5.0 # Antes 12.0 (Movimiento más pausado)
        self.action_timer = 0.0

    def move_towards(self, tx, ty):
        self.target_x, self.target_y = tx, ty

    def update(self, dt: float):
        # ... (movimiento igual) ...
        # 2. Lógica de IA (Decisiones)
        self.action_timer += dt
        if self.action_timer > 2.5: # Antes 1.0 (Deciden cada 2.5 segundos)
            self.action_timer = 0
            self._logic_tick()

    def _logic_tick(self):
        # Fatiga por actividad
        if self.state != "RESTING": self.energy -= 1

        # MÁQUINA DE ESTADOS
        if self.state == "RESTING":
            self.energy += 15
            if self.energy >= 100:
                self.energy = 100
                self.state = "IDLE"
                logger.log(f"{self.name} se despertó con energía.")

        elif self.energy < 20:
            self.state = "GOING_HOME"
            self.move_towards(0, 0)
            logger.log(f"{self.name} tiene sueño. Vuelve a casa.")

        elif self.state == "IDLE":
            if random.random() < 0.3:
                self.state = "SEARCHING"
                # Elegir un punto aleatorio en el mapa
                tx, ty = random.randint(-15, 15), random.randint(-15, 15)
                self.move_towards(tx, ty)
                logger.log(f"{self.name} salió a buscar madera.")

        elif self.state == "SEARCHING":
            dist_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
            if dist_to_target < 0.5:
                # Llegó a destino, recolectar
                self.state = "GATHERING"
                logger.log(f"{self.name} encontró algo y está trabajando...")

        elif self.state == "GATHERING":
            self.inventory["wood"] += 1
            if self.inventory["wood"] >= 3:
                self.state = "GOING_HOME"
                self.move_towards(0, 0)
                logger.log(f"{self.name} recolectó madera y vuelve al hogar.")

        elif self.state == "GOING_HOME":
            dist_home = math.sqrt(self.x**2 + self.y**2)
            if dist_home < 0.5:
                # Entregó madera
                if self.inventory["wood"] > 0:
                    logger.log(f"✨ {self.name} entregó {self.inventory['wood']} de madera.")
                    self.inventory["wood"] = 0
                
                if self.energy < 50:
                    self.state = "RESTING"
                    logger.log(f"{self.name} se fue a dormir.")
                else:
                    self.state = "IDLE"
