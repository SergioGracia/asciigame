from ...core.state import WorldState
from ...core.entities.person import Person

def ascii_renderer(world_state: WorldState):
    """Interfaz ASCII simple que imprime el estado en la terminal."""
    print(f"--- TICK: {world_state.tick_count} ---")
    entities = world_state.get_all_entities()
    if not entities:
        print("El mundo está vacío...")
    for entity in entities:
        info = f"[{entity.name}] - Posición: ({entity.x}, {entity.y})"
        if isinstance(entity, Person):
            info += f" | Energía: {entity.energy}"
        print(info)
    print("-" * 20)
