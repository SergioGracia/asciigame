import sys
import os
import curses
import random

# Asegurar path para importaciones relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.entities.town import Town
from src.core.entities.person import Person
from src.core.entities.wolf import Wolf
from src.core.entities.shop import Shop
from src.core.state import WorldState
from src.core.engine import SimulationEngine
from src.interfaces.cli.curses_renderer import CursesRenderer
from src.core.persistence import PersistenceManager
from src.core.logger import logger

# ESCENARIOS
from src.core.scenarios.nature import NatureScenario
from src.core.scenarios.urban import UrbanScenario

def main(stdscr):
    """Bucle principal gestionado por curses."""
    
    # ---------------------------------------------------------
    # ESCENARIO ACTIVO: NATURE (Bosque)
    scenario = NatureScenario()
    # ---------------------------------------------------------

    world = WorldState(scenario)
    
    # 1. Base / Hogar
    hx, hy = 0, 0
    home = Town("Hogar Central", x=hx, y=hy)
    world.add_entity(home)
    
    # 2. Tienda
    shop = Shop(hx + 10, hy + 10)
    world.add_entity(shop)

    # 3. Peligros (Lobos)
    for i in range(3):
        wx, wy = random.uniform(-80, 80), random.uniform(-80, 80)
        world.add_entity(Wolf(f"Lobo {i}", x=wx, y=wy))
    
    # 4. Población MASIVA (8 Personajes para pruebas rápidas)
    nombres = ["Juan", "Maria", "Pedro", "Lucia", "Diego", "Ana", "Luis", "Elena"]
    for i, nombre in enumerate(nombres):
        # Repartirlos por el mapa
        px = random.uniform(-30, 30)
        py = random.uniform(-30, 30)
        p = Person(nombre, x=px, y=py, goal=random.choice(["BUILDER", "TRADER"]))
        p.inventory["wood"] = 10 # Empiezan con recursos
        if nombre == "Juan": p.is_leader = True
        world.add_entity(p)
    
    # 5. Motor y Renderer
    engine = SimulationEngine(world, fps=20)
    renderer = CursesRenderer(stdscr)
    
    def wrapped_renderer(ws):
        renderer.render(ws)
        stdscr.nodelay(True)
        key = stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            engine.stop()
        elif key == ord('s') or key == ord('S'):
            PersistenceManager.save_game(world)
            logger.log("SYS: Partida guardada correctamente.")
        elif key == ord('n') or key == ord('N'):
            people = [e for e in ws.get_all_entities() if isinstance(e, Person)]
            if renderer.camera_focus in people:
                idx = (people.index(renderer.camera_focus) + 1) % len(people)
                renderer.camera_focus = people[idx]
        elif key == ord('h') or key == ord('H'):
            renderer.toggle_legend()

    engine.register_render_callback(wrapped_renderer)
    engine.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
