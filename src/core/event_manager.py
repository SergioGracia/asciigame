import random
from .logger import logger
from .entities.person import Person
from .state import WorldState

class EventManager:
    """Clase para inyectar eventos aleatorios basados en el estado del mundo."""
    def __init__(self, world_state: WorldState):
        self.world_state = world_state
        self.events = [
            self._mugging_event,
            self._court_summons,
            self._tax_inspector,
            self._good_finding
        ]

    def update(self):
        """Intenta lanzar un evento aleatorio si se cumplen las condiciones."""
        entities = [e for e in self.world_state.get_all_entities() if isinstance(e, Person)]
        if not entities: return

        # 2% de probabilidad por tick lógico (Antes 5%)
        if random.random() < 0.02:
            event_func = random.choice(self.events)
            event_func(random.choice(entities))

    def _mugging_event(self, victim: Person):
        if victim.wealth > 10:
            stolen = random.randint(5, victim.wealth)
            victim.wealth -= stolen
            victim.stress += 30
            logger.log(f"¡{victim.name} ha sido atracado! Perdió {stolen} de oro.")
        else:
            logger.log(f"Un ladrón intentó atracar a {victim.name}, pero es demasiado pobre.")

    def _court_summons(self, victim: Person):
        victim.stress += 20
        logger.log(f"⚖️ {victim.name} recibió citación judicial por ruido.")

    def _tax_inspector(self, victim: Person):
        tax = int(victim.wealth * 0.2)
        victim.wealth -= tax
        logger.log(f"🕵️ Hacienda: {victim.name} pagó {tax} de impuestos.")

    def _good_finding(self, person: Person):
        found = random.randint(5, 15)
        person.wealth += found
        logger.log(f"✨ {person.name} encontró {found} de oro en el suelo.")
