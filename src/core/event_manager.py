import random
from .logger import logger
from .entities.person import Person
from .state import WorldState

class EventManager:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state
        self.events = [
            self._mugging_event,
            self._court_summons,
            self._tax_inspector,
            self._good_finding,
            self._lottery_win,
            self._existential_crisis,
            self._found_relic,
            self._bad_flu
        ]

    def update(self):
        entities = [e for e in self.world_state.get_all_entities() if isinstance(e, Person)]
        if not entities: return

        if random.random() < 0.03: # Probabilidad ajustada
            event_func = random.choice(self.events)
            event_func(random.choice(entities))

    def _mugging_event(self, victim: Person):
        if victim.wealth > 15:
            stolen = random.randint(5, 15)
            victim.wealth -= stolen
            victim.stress += 30
            logger.log(f"ALARM: {victim.name} ha sido atracado! Perdio {stolen}G.")
        else:
            logger.log(f"{victim.name} esquivo un intento de atraco por ser pobre.")

    def _court_summons(self, victim: Person):
        victim.stress += 20
        logger.log(f"COURT: {victim.name} recibio una citacion judicial.")

    def _tax_inspector(self, victim: Person):
        tax = int(victim.wealth * 0.15)
        victim.wealth -= tax
        logger.log(f"TAX: Hacienda ha cobrado {tax}G a {victim.name}.")

    def _good_finding(self, person: Person):
        found = random.randint(5, 10)
        person.wealth += found
        logger.log(f"GOLD: {person.name} encontro una bolsa con {found}G.")

    def _lottery_win(self, person: Person):
        win = random.randint(50, 100)
        person.wealth += win
        person.stress -= 10
        logger.log(f"GOLD: ¡{person.name} ha ganado la loteria! +{win}G.")

    def _existential_crisis(self, person: Person):
        person.stress += 40
        logger.log(f"CRISIS: {person.name} sufre una crisis existencial. Stress alto.")

    def _found_relic(self, person: Person):
        person.wealth += 30
        logger.log(f"GOLD: {person.name} hallo una reliquia antigua valiosa.")

    def _bad_flu(self, person: Person):
        person.energy = max(0, person.energy - 40)
        logger.log(f"ALARM: {person.name} ha pillado una gripe fuerte. Energia baja.")
