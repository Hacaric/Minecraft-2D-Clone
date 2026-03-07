from entityAI import *

class EntityType:
    def __init__(self, type_id: str, name: str, width: float, height: float, texture: str = None, max_health: int = 100, ai_class=NoAI, default_variation=0):
        """
        Blueprint for an entity type.
        :param type_id: Unique identifier for the type (e.g., "zombie").
        :param name: Display name of the entity.
        :param width: Default hitbox width.
        :param height: Default hitbox height.
        :param texture: Default texture filename.
        :param max_health: Base health for this type.
        :param ai_class: The AI behavior class for this entity.
        """
        self.type_id = type_id
        self.name = name
        self.width = width
        self.height = height
        self.texture = texture
        self.max_health = max_health
        self.ai_class = ai_class
        self.default_variation = 0

class EntityTypes:
    """Registry of all available entity types."""
    
    NONE = EntityType("none", "None", 0, 0, "undefined.png", 1, ai_class=NoAI)
    PLAYER = EntityType("player", "Player", 0.4, 1.8, "steve.png", 100, ai_class=NoAI) # Player controlled by input, not AI
    ZOMBIE = EntityType("zombie", "Zombie", 0.6, 1.8, "zombie.png", 20, ai_class=HostileAI)
    PIG = EntityType("pig", "Pig", 0.9, 0.9, "pig.png", 10, ai_class=PassiveAI)
    ITEM = EntityType("item", "Item", 0.25, 0.25, None, 1, ai_class=ItemAI)

    _registry = {
        "player": PLAYER,
        "zombie": ZOMBIE,
        "pig": PIG,
        "item": ITEM
    }

    @classmethod
    def get(cls, type_id: str) -> EntityType:
        """Retrieve an EntityType by its string ID."""
        return cls._registry.get(type_id)
