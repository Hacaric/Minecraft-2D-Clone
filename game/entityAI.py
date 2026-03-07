from _config import Constants

class EntityAI:
    def __init__(self):
        pass

    def update(self, entity, world):
        """
        Main logic for the AI. 
        :param entity: The entity instance this AI is controlling.
        :param world: The world instance for sensing surrounding blocks/players.
        """
        pass

class PassiveAI(EntityAI):
    """Simple AI that wanders around aimlessly."""
    def update(self, entity, world):
        # Placeholder for wandering logic
        pass

class HostileAI(EntityAI):
    """AI that chases the nearest player."""
    def update(self, entity, world):
        # Placeholder for chasing logic
        pass

class ItemAI(EntityAI):
    """For items, or any pickable entities"""
    def update(self, entity, world):
        # if entity.y < -500:
        #     entity.die()

        if not world.on_ground(entity.hitbox):
            entity.velocityY += Constants.Player.gravity
        else:
            entity.velocityY = 0 

        if world.hitboxCollide(entity.hitbox):
            # TODO: go to nearest free space
            entity.y += 0.1

        old_pos = entity.getPos()
        for _ in range(3):
            entity.moveBy(entity.velocityX, 0)
            if world.hitboxCollide(entity.hitbox):
                entity.x, entity.y = old_pos
                entity.velocityX = round(entity.velocityX/2, 3)
            else:
                break

        old_pos = entity.getPos()
        for _ in range(3):
            entity.moveBy(0, entity.velocityY)
            if world.hitboxCollide(entity.hitbox):
                entity.x, entity.y = old_pos
                entity.velocityY = round(entity.velocityY/2, 3)
            else:
                break
        
        entity.velocityX = round(entity.velocityX, 3)
        entity.velocityY = round(entity.velocityY, 3)
        entity.x = round(entity.x, 3)
        entity.y = round(entity.y, 3)
        

class NoAI(EntityAI):
    """For entities that don't move or act."""
    def update(self, entity, world):
        pass