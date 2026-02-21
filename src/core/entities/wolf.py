import random
import math
from .base import Entity

class Wolf(Entity):
    def __init__(self, name: str, x: float, y: float):
        super().__init__(name, x, y)
        self.speed = 3.0
        self.target_x = x + random.uniform(-10, 10)
        self.target_y = y + random.uniform(-10, 10)
        self.decision_timer = 0.0

    def update(self, dt: float, is_night: bool = False, world_state=None):
        # 1. Movimiento de patrulla
        current_speed = self.speed * 2.5 if is_night else self.speed
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.5:
            step = current_speed * dt
            nx = self.x + (dx / dist) * step
            ny = self.y + (dy / dist) * step
            
            # CONSULTAR WORLD_STATE PARA RESPETAR MUROS X
            can_move = True
            if world_state:
                can_move = world_state.is_walkable(nx, ny)
            
            if can_move:
                self.x, self.y = nx, ny
            else:
                # Si choca con un muro, cambia de objetivo inmediatamente
                self.target_x = self.x + random.uniform(-30, 30)
                self.target_y = self.y + random.uniform(-30, 30)
        else:
            self.decision_timer += dt
            if self.decision_timer > 3.0:
                self.decision_timer = 0
                self.target_x = self.x + random.uniform(-40, 40)
                self.target_y = self.y + random.uniform(-40, 40)
