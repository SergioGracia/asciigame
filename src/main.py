import sys
import os
import curses
import random

# Asegurar path para importaciones relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.entities.base import Entity
from src.core.entities.person import Person
from src.core.state import WorldState
from src.core.engine import SimulationEngine
from src.interfaces.cli.curses_renderer import CursesRenderer

def main(stdscr):
    """Bucle principal gestionado por curses."""
    world = WorldState()
    
    # 1. Añadir el Hogar (Punto de entrega)
    world.add_entity(Entity("Hogar", x=0, y=0))
    
    # 2. Generar Población Masiva (15 Ciudadanos)
    nombres = ["Juan", "Maria", "Pedro", "Lucia", "Diego", "Elena", "Mario", "Sofia", 
               "Carlos", "Ana", "Luis", "Marta", "Ramon", "Ines", "Jose"]
    
    for nombre in nombres:
        # Repartirlos un poco por el mapa inicial
        rx = random.uniform(-15, 15)
        ry = random.uniform(-15, 15)
        world.add_entity(Person(nombre, x=rx, y=ry))
    
    # 3. Configuración del motor (20 FPS para fluidez)
    engine = SimulationEngine(world, fps=20)
    
    # 4. Registrar el renderer
    renderer = CursesRenderer(stdscr)
    
    def wrapped_renderer(ws):
        renderer.render(ws)
        # Salida por teclado
        stdscr.nodelay(True)
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            engine.stop()
        # Cambiar foco de cámara con 'n' (Next)
        elif key == ord('n') or key == ord('N'):
            people = [e for e in ws.get_all_entities() if isinstance(e, Person)]
            if renderer.camera_focus in people:
                idx = (people.index(renderer.camera_focus) + 1) % len(people)
                renderer.camera_focus = people[idx]

    engine.register_render_callback(wrapped_renderer)
    
    # Iniciar
    engine.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
