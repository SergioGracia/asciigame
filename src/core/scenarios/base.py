from typing import Dict, List, Tuple, Any

class BaseScenario:
    name: str = "Base"
    biomes_def: Dict[str, Dict[str, Any]] = {}
    legend_def: List[Tuple[str, str, int]] = []
    structures_blueprints: Dict[str, List[Tuple[int, int, str, int, bool]]] = {}

    def get_biome_id(self, x: float, y: float) -> str: raise NotImplementedError
    def generate_decorations(self, radius: int) -> Dict[Tuple[int, int], str]: raise NotImplementedError
    def get_home_coords(self) -> Tuple[int, int]: return (0, 0) # Por defecto el origen

    def is_door(self, x: int, y: int) -> bool: return False
    def get_ground_char(self, biome_id: str) -> str:
        return self.biomes_def.get(biome_id, {}).get("char", ".")
    def get_biome_stats(self, biome_id: str) -> Dict[str, Any]:
        return self.biomes_def.get(biome_id, {})
    def is_walkable(self, x: float, y: float) -> bool:
        bx, by = int(x), int(y)
        if self.is_door(bx, by): return True
        biome = self.get_biome_id(x, y)
        return not self.biomes_def.get(biome, {}).get("solid", False)
