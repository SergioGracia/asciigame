from .base import Entity

class Town(Entity):
    def __init__(self, name: str, x: int = 0, y: int = 0):
        super().__init__(name, x, y)
        self.resources = {"wood": 0, "food": 0}

    def deposit(self, resource: str, amount: int):
        if resource in self.resources:
            self.resources[resource] += amount
            return True
        return False

    def __repr__(self):
        return f"<Town name={self.name} resources={self.resources}>"
