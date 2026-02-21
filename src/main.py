import sys
import os
import curses
import random

# Asegurar path para importaciones relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.entities.town import Town
from src.core.entities.person import Person
from src.core.entities.wolf import Wolf
from src.core.state import WorldState
from src.core.engine import SimulationEngine
from src.interfaces.cli.curses_renderer import CursesRenderer

# ESCENARIOS
from src.core.scenarios.nature import NatureScenario
from src.core.scenarios.urban import UrbanScenario

def main(stdscr):
    """Bucle principal gestionado por curses."""
    
    # ---------------------------------------------------------
    # ESCENARIO POR DEFECTO: NATURE
    scenario = NatureScenario()
    # ---------------------------------------------------------

    world = WorldState(scenario)
    
    # 1. Base / Hogar
    home = Town("Hogar", x=0, y=0)
    world.add_entity(home)

    # 2. Peligros (Lobos)
    for i in range(3):
        wx, wy = random.uniform(-50, 50), random.uniform(-50, 50)
        world.add_entity(Wolf(f"Lobo {i}", x=wx, y=wy))
    
    # 3. Población (Juan y Maria)
    world.add_entity(Person("Juan", x=10, y=10, goal="BUILDER"))
    world.add_entity(Person("Maria", x=-10, y=-10, goal="TRADER"))
    
    # 4. Motor y Renderer
    engine = SimulationEngine(world, fps=20)
    renderer = CursesRenderer(stdscr)
    
    def wrapped_renderer(ws):
        renderer.render(ws)
        stdscr.nodelay(True)
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            engine.stop()
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
