import uuid

class Entity:
    """Clase base para todos los objetos del simulador."""
    def __init__(self, name: str, x: int = 0, y: int = 0):
        self.id = uuid.uuid4()
        self.name = name
        self.x = x
        self.y = y

    def update(self, delta_time: float):
        """Método para actualizar el estado de la entidad cada tick."""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} id={self.id} pos=({self.x},{self.y})>"
