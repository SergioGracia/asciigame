import random
import math
from .base import Entity

class Wolf(Entity):
    """Entidad hostil (Lobo en Nature, Coche en Urban)."""
    def __init__(self, name: str, x: float, y: float):
        super().__init__(name, x, y)
        self.speed = 3.0
        self.target_x = x + random.uniform(-10, 10)
        self.target_y = y + random.uniform(-10, 10)
        self.decision_timer = 0.0

    def update(self, dt: float, is_night: bool = False, scenario=None):
        # 1. Movimiento de patrulla
        current_speed = self.speed * 2.5 if is_night else self.speed
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.5:
            step = current_speed * dt
            
            # PREDICCIÓN Y COLISIÓN
            next_x = self.x + (dx / dist) * step
            next_y = self.y + (dy / dist) * step
            
            can_move = True
            if scenario:
                can_move = scenario.is_walkable(next_x, next_y)
            
            if can_move:
                self.x = next_x
                self.y = next_y
            else:
                # Si choca, cambia de rumbo inmediatamente
                self.target_x = self.x + random.uniform(-20, 20)
                self.target_y = self.y + random.uniform(-20, 20)
        else:
            self.decision_timer += dt
            decision_limit = 2.0 if is_night else 5.0
            if self.decision_timer > decision_limit:
                self.decision_timer = 0
                self.target_x += random.uniform(-20, 20)
                self.target_y += random.uniform(-20, 20)

    def __repr__(self):
        return f"<Hostile pos=({self.x},{self.y})>"
