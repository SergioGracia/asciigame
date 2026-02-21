import random

class Storyteller:
    """Transforma eventos crudos en narrativa profunda."""
    
    def narrate(self, raw_message: str) -> str:
        # Si no tiene prefijo, lo devolvemos tal cual (o lo embellecemos levemente)
        if ":" not in raw_message:
            return raw_message

        prefix, content = raw_message.split(":", 1)
        content = content.strip()
        
        if prefix == "GOLD":
            templates = [
                f"La fortuna brilla: {content}.",
                f"Un destello en el suelo revela que {content}.",
                f"El destino ha querido que {content}."
            ]
            return random.choice(templates)
            
        elif prefix == "ALARM" or prefix == "CRISIS":
            templates = [
                f"¡Peligro! {content}",
                f"El corazón se acelera: {content}",
                f"En un giro dramático, {content}"
            ]
            return random.choice(templates)
            
        elif prefix == "ZEN" or prefix == "TALK":
            templates = [
                f"En un momento de paz, {content}",
                f"Las palabras fluyen: {content}",
                f"{content} (La conexión se fortalece)."
            ]
            return random.choice(templates)
            
        elif prefix == "BUILD":
            return f"El progreso continúa: {content}"

        return f"[{prefix}] {content}" # Fallback
