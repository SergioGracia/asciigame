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

from src.core.scenarios.nature import NatureScenario
from src.core.scenarios.urban import UrbanScenario
from src.core.scenarios.cave import CaveScenario

def main(stdscr):
    """Bucle principal gestionado por curses."""
    
    # 1. ESTADO DE ESCENARIOS
    surface_scenario = NatureScenario()
    cave_scenario = None # Se generará al entrar
    active_scenario = surface_scenario
    
    world = WorldState(active_scenario)
    
    # Posición guardada en la superficie
    surface_pos = (0.0, 0.0)
    
    # 2. Punto de Foco Cámara (Tienda solitaria)
    focus_point = Shop(0, 0)
    world.add_entity(focus_point)

    # 3. Motor y Renderer
    engine = SimulationEngine(world, fps=15)
    renderer = CursesRenderer(stdscr)
    renderer.camera_focus = focus_point
    
    def wrapped_renderer(ws):
        nonlocal active_scenario, cave_scenario, surface_pos
        renderer.render(ws)
        stdscr.nodelay(True)
        key = stdscr.getch()
        
        # MOVIMIENTO DE CÁMARA
        move_speed = 5.0 * renderer.zoom
        if key in [ord('w'), ord('W'), curses.KEY_UP]:
            focus_point.y -= move_speed
        elif key in [ord('s'), ord('S'), curses.KEY_DOWN]:
            focus_point.y += move_speed
        elif key in [ord('a'), ord('A'), curses.KEY_LEFT]:
            focus_point.x -= move_speed
        elif key in [ord('d'), ord('D'), curses.KEY_RIGHT]:
            focus_point.x += move_speed
            
        # ACCIÓN ESPECIAL: ENTRAR / SALIR (E)
        if key in [ord('e'), ord('E')]:
            # Comprobar qué hay bajo los pies
            char = active_scenario.get_ground_char(int(focus_point.x), int(focus_point.y), 
                                                active_scenario.get_biome_id(focus_point.x, focus_point.y))
            
            if char == "0":
                if active_scenario == surface_scenario:
                    # ENTRAR A CUEVA
                    logger.log("DESCEND: Entrando a las profundidades...")
                    surface_pos = (focus_point.x, focus_point.y)
                    cave_scenario = CaveScenario(seed=surface_scenario.seed + int(focus_point.x + focus_point.y))
                    active_scenario = cave_scenario
                    ws.scenario = active_scenario
                    focus_point.x, focus_point.y = 0, 0 # Empezar en el centro del submundo
                else:
                    # SALIR A SUPERFICIE
                    logger.log("ASCEND: Volviendo a la superficie...")
                    active_scenario = surface_scenario
                    ws.scenario = active_scenario
                    focus_point.x, focus_point.y = surface_pos[0], surface_pos[1]

        if key == ord('q') or key == ord('Q'):
            engine.stop()
        elif key == ord('s') or key == ord('S'):
            PersistenceManager.save_game(world)
            logger.log("SYS: Partida guardada correctamente.")
        elif key in [ord('+'), ord('=')]:
            renderer.zoom = max(0.1, renderer.zoom * 0.8)
            logger.log(f"ZOOM: Acercando (x{1.0/renderer.zoom:.1f})")
        elif key in [ord('-'), ord('_')]:
            renderer.zoom = min(50.0, renderer.zoom * 1.2)
            logger.log(f"ZOOM: Alejando (x{1.0/renderer.zoom:.1f})")
        elif key == ord('h') or key == ord('H'):
            renderer.toggle_legend()

    engine.register_render_callback(wrapped_renderer)
    engine.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
