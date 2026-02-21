from .base import Entity
from ..logger import logger

class Shop(Entity):
    def __init__(self, x, y):
        super().__init__("Tienda General", x, y)
        self.stock = {"food": 100, "medkit": 50, "shoes": 10}
        self.prices = {"food": 5, "medkit": 20, "shoes": 50}

    def interact(self, buyer):
        """Intenta vender algo al comprador según su necesidad."""
        # 0. CURAR ENFERMEDAD
        if buyer.disease and buyer.wealth >= 15:
            buyer.wealth -= 15
            buyer.disease = None
            logger.log(f"SHOP: {buyer.name} compro medicinas y se curo (-15G).")
            return

        # 1. SALUD -> Medkit (Estrés)
        if buyer.stress > 40 and buyer.wealth >= 20:
            if self._sell("medkit", buyer):
                buyer.stress = 0
                logger.log(f"SHOP: {buyer.name} compro medicinas (-20G).")
                return

        # 2. ENERGIA -> Comida
        if buyer.energy < 50 and buyer.wealth >= 5:
            if self._sell("food", buyer):
                buyer.energy = 100
                logger.log(f"SHOP: {buyer.name} compro comida (-5G).")
                return

        # 3. LUJO -> Zapatos (Velocidad)
        if buyer.wealth >= 60:
            if self._sell("shoes", buyer):
                buyer.base_speed += 1.0
                logger.log(f"SHOP: {buyer.name} compro botas nuevas! (+Speed).")
                buyer.add_journal_entry("Me compre unas botas de lujo.")

    def _sell(self, item, buyer):
        if self.stock.get(item, 0) > 0 and buyer.wealth >= self.prices[item]:
            buyer.wealth -= self.prices[item]
            self.stock[item] -= 1
            # buyer.inventory[item]... (Ya lo usamos directamente)
            return True
        return False
