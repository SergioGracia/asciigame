import random
import math
from .logger import logger

class EventRegistry:
    def __init__(self):
        # Cada evento: (probabilidad, plantilla, efectos, condicion_lambda)
        # La condicion recibe (persona, world_state)
        self.event_pool = [
            # --- CLIMA (Solo si está fuera) ---
            (0.01, "WEATHER: El olor a tierra mojada relaja a {name}.", {"stress": -5}, 
             lambda p, ws: self._is_outside(p)),
            (0.005, "WEATHER: Un rayo cae sobre un arbol cerca de {name}!", {"stress": 30}, 
             lambda p, ws: self._is_outside(p) and ws.scenario.get_biome_id(p.x, p.y) == "FOREST"),
            (0.01, "WEATHER: La niebla impide que {name} vea bien.", {"speed_mult": 0.6}, 
             lambda p, ws: self._is_outside(p)),

            # --- FINANZAS (Contextuales) ---
            (0.01, "GOLD: {name} encontro una moneda en el asfalto.", {"wealth": 2}, 
             lambda p, ws: ws.scenario.get_biome_id(p.x, p.y) == "STREET"),
            (0.005, "TAX: Un inspector de hacienda abordo a {name} en la oficina.", {"wealth": -20, "stress": 15}, 
             lambda p, ws: ws.scenario.get_biome_id(p.x, p.y) == "INTERIOR"),

            # --- SOCIAL (¡Solo si hay alguien cerca!) ---
            (0.02, "TALK: {name} discutio con un vecino por un malentendido.", {"stress": 20}, 
             lambda p, ws: self._is_near_anyone(p, ws)),
            (0.02, "TALK: Un transeunte elogio el aspecto de {name}.", {"stress": -10}, 
             lambda p, ws: self._is_near_anyone(p, ws)),
            (0.01, "GOSSIP: {name} escucho un secreto de alguien cercano.", {"stress": -5}, 
             lambda p, ws: self._is_near_anyone(p, ws)),

            # --- NATURALEZA ---
            (0.01, "ZEN: {name} se quedo mirando el fluir del agua.", {"stress": -20}, 
             lambda p, ws: ws.scenario.get_biome_id(p.x, p.y) == "WATER"),
            (0.01, "OOPS: {name} se pincho con un cactus.", {"energy": -5, "stress": 5}, 
             lambda p, ws: ws.scenario.get_biome_id(p.x, p.y) == "DESERT"),
            (0.01, "BUILD: {name} encontro madera de calidad superior.", {"energy": 10}, 
             lambda p, ws: ws.scenario.get_biome_id(p.x, p.y) == "FOREST"),

            # --- ESTADO INTERNO (Siempre posibles) ---
            (0.005, "CRISIS: {name} reflexiona sobre el sentido de su existencia.", {"stress": 15}, 
             lambda p, ws: p.stress > 40),
            (0.01, "ZEN: {name} siente un repentino optimismo.", {"stress": -15}, 
             lambda p, ws: p.energy > 80)
        ]

    # --- AYUDANTES DE CONDICIÓN ---
    def _is_outside(self, p):
        # En Urban, INTERIOR es dentro. En Nature, asumimos que siempre está fuera 
        # a menos que esté en el origen (hogar).
        from .entities.person import Person
        rel_x, rel_y = (int(p.x) + 15) % 30 - 15, (int(p.y) + 15) % 30 - 15
        is_in_building = abs(rel_x) < 6 and abs(rel_y) < 6
        return not is_in_building

    def _is_near_anyone(self, p, ws):
        from .entities.person import Person
        for entity in ws.get_all_entities():
            if isinstance(entity, Person) and entity.id != p.id:
                dist = math.sqrt((p.x - entity.x)**2 + (p.y - entity.y)**2)
                if dist < 4.0: return True
        return False

    def get_random_event(self, person, world_state):
        triggered = []
        for prob, template, effects, condition in self.event_pool:
            if random.random() < prob:
                # SOLO DISPARA SI SE CUMPLE LA CONDICIÓN
                if condition(person, world_state):
                    triggered.append((template, effects))
        return triggered

    def apply_event(self, person, event_data):
        template, effects = event_data
        
        # LUCKY: 50% de ignorar lo malo
        is_bad = any(v < 0 for v in effects.values() if isinstance(v, (int, float))) or effects.get("stress", 0) > 0
        if "LUCKY" in person.traits and is_bad and random.random() < 0.5:
            logger.log(f"ZEN: La suerte de {person.name} le libro de un mal trago.")
            return

        # MODIFICADORES POR RASGOS
        final_effects = effects.copy()
        if "GREEDY" in person.traits:
            if "wealth" in final_effects and final_effects["wealth"] > 0:
                final_effects["wealth"] *= 2 # Gana el doble
            if "wealth" in final_effects and final_effects["wealth"] < 0:
                final_effects["stress"] = final_effects.get("stress", 0) + 20 # Le duele mas perder
        
        if "BRAVE" in person.traits and "stress" in final_effects and final_effects["stress"] > 0:
            final_effects["stress"] *= 0.5 # Le estresa la mitad

        # Aplicar efectos finales
        if "stress" in final_effects: person.stress = max(0, person.stress + final_effects["stress"])
        if "energy" in final_effects: person.energy = max(0, min(100, person.energy + final_effects["energy"]))
        if "wealth" in final_effects: person.wealth = max(0, person.wealth + final_effects["wealth"])
        if "speed_mult" in final_effects: person.speed *= final_effects["speed_mult"]
        
        message = template.format(name=person.name)
        logger.log(message)
