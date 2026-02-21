import heapq
import math

class Pathfinder:
    def __init__(self, world_state):
        self.world_state = world_state

    def get_path(self, start, end, max_steps=400):
        sx, sy = int(start[0]), int(start[1])
        ex, ey = int(end[0]), int(end[1])
        
        # Si la meta es sólida, buscar el punto libre más cercano
        if not self.world_state.is_walkable(ex, ey):
            found = False
            for r in range(1, 6):
                for dx, dy in [(-r,0), (r,0), (0,-r), (0,r)]:
                    if self.world_state.is_walkable(ex+dx, ey+dy):
                        ex, ey = ex+dx, ey+dy
                        found = True; break
                if found: break
            if not found: return []

        open_set = []
        heapq.heappush(open_set, (0, (sx, sy)))
        came_from = {}
        g_score = {(sx, sy): 0}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == (ex, ey):
                return self._reconstruct_path(came_from, current)
            
            # ESTRICTAMENTE 4 DIRECCIONES
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if not self.world_state.is_walkable(neighbor[0], neighbor[1]):
                    continue
                    
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    priority = tentative_g + abs(neighbor[0]-ex) + abs(neighbor[1]-ey)
                    heapq.heappush(open_set, (priority, neighbor))
                    
        return []

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
