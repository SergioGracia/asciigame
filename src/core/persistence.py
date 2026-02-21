import pickle
import gzip
import os
from datetime import datetime
from .state import WorldState

SAVE_DIR = "saves"

class PersistenceManager:
    @staticmethod
    def save_game(world_state: WorldState, filename: str = None):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.dat"
            
        filepath = os.path.join(SAVE_DIR, filename)
        
        try:
            # Serializamos y comprimimos el estado completo
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(world_state, f)
            print(f"Game saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save game: {e}")
            return None

    @staticmethod
    def load_game(filename: str) -> WorldState:
        filepath = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(filepath):
            print("Save file not found.")
            return None
            
        try:
            with gzip.open(filepath, 'rb') as f:
                world_state = pickle.load(f)
            print(f"Game loaded from {filepath}")
            return world_state
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
