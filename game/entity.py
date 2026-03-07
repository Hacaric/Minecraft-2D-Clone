from gameLogger import log
import pygame
import json
from _config import Constants
from inventory import *
import math
from entityType import EntityTypes

def convert_to_type(object, target_type):
    return target_type(object)

class Hitbox:
    def __init__(self, x, y, width, height, velocityX = 0, velocityY = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocityX = velocityX
        self.velocityY = velocityY

class Entity:
    def __init__(self, x, y, entity_type, variation=0, id=None):
        self.entity_type = entity_type
        self.hitbox = Hitbox(x, y, entity_type.width, entity_type.height)
        self.name = entity_type.name
        self.texture = entity_type.texture
        self.entity_type_id = entity_type.type_id
        self.variation = variation
        self.id = id
        self.spawn_tick = None
        
        # Initialize AI behavior from bluelog
        self.ai = entity_type.ai_class()

        # Define which attributes to save. We can extend this in subclasses.
        self._savable_attributes = [["name", str], ["entity_type_id", str], ["variation", int], ["id",str]]
        self._savable_hitbox_attributes = [["x", float], ["y", float], ["width", float], ["width", float], ["velocityX", float], ["velocityY", float]]

    def setID(self, id, tick):
        self.id = id
        self.spawn_tick = tick

    def tick(self, world):
        """Called every frame to update entity logic/AI."""
        if not self.id:
            log(f"Cannot tick entity {self.entity_type.type_id} without id, use entity.setID first!")
            return
        
        if self.ai:
            self.ai.update(self, world)

    def distance(self, entity:Entity):
        return math.hypot(self.x - entity.x, self.y - entity.y)

    def getPos(self):
        return self.x, self.y

    def moveBy(self, x, y):
        self.x += x
        self.y += y

    def moveTo(self, x, y):
        self.x = x
        self.y = y

    def newHitbox(self, x, y, width, height):
        self.hitbox = Hitbox(x, y, width, height)

    def getHitbox(self):
        return self.hitbox

    def parse(self) -> str:
        parsed_data = {}
        for attr in self._savable_attributes:
            parsed_data[attr[0]] = str(getattr(self, attr[0]))
        for attr in self._savable_hitbox_attributes:
            parsed_data[attr[0]] = str(getattr(self.hitbox, attr[0]))
            # log(f"Setting hitbox attr {attr[0]} to {parsed_data[attr[0]]}")
        return json.dumps(parsed_data)

    def load(self, data:str):
        parsed_data = json.loads(data)
        for attribute in self._savable_attributes:
            if attribute[0] in parsed_data:
                setattr(self, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
                log(f"Loading attr {attribute[0]}: {parsed_data[attribute[0]]}")
        for attribute in self._savable_hitbox_attributes:
            if attribute[0] in parsed_data:
                setattr(self.hitbox, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
                log(f"Loading hitbox attr {attribute[0]}: {parsed_data[attribute[0]]}")
        
        # Re-initialize type and AI if type_id changed during load
        if "entity_type_id" in parsed_data:
            self.entity_type = EntityTypes.get(parsed_data["entity_type_id"])
            if self.entity_type:
                self.ai = self.entity_type.ai_class()

    def debug_info(self, world):
        return f"Debug info about entity id:{self.id} on X:{self.x}, Y:{self.y} of entity type {self.entity_type.name}."
    
    @property
    def x(self): return self.hitbox.x

    @x.setter
    def x(self, value): self.hitbox.x = value

    @property
    def y(self): return self.hitbox.y

    @y.setter
    def y(self, value): self.hitbox.y = value
    
    @property
    def width(self): return self.hitbox.width

    @width.setter
    def width(self, value): self.hitbox.width = value
    
    @property
    def height(self): return self.hitbox.height

    @height.setter
    def height(self, value): self.hitbox.height = value

    @property
    def velocityX(self):
        return self.hitbox.velocityX
    
    @velocityX.setter
    def velocityX(self, value):
        self.hitbox.velocityX = value
        
    @property
    def velocityY(self):
        return self.hitbox.velocityY
    
    @velocityY.setter
    def velocityY(self, value):
        self.hitbox.velocityY = value

def LoadEntityFromString(data):
    log(f"Loading entity from string!")
    entity = Entity(0,0,EntityTypes.NONE)
    entity.load(data)
    if entity.entity_type_id == EntityTypes.PLAYER.type_id:
        log(f"Entity was player, creating player instance! (name:{entity.name})")
        player = Player("", 0, 0)
        player.load(data)
        log(f"Loaded player: {player.name}")
        return player
    return entity

class MovementRequests:
    def __init__(self, up:bool, down:bool, right:bool, left:bool):
        self.up = up
        self.down = down
        self.right = right
        self.left = left

class MovementRequest_NoInput(MovementRequests):
    def __init__(self):
        super().__init__(*[False for _ in range(4)])

class Player(Entity):
    def __init__(self, name, x=0, y=0, role="user", gamemode=0): # role: "user" or "admin"
        super().__init__(x, y, EntityTypes.PLAYER)
        self.name = name
        self.gamemode = int(gamemode)
        self._savable_attributes.extend([["role", str], ["maxHealth", int], ["health", int], ["alive", bool]])
        self.role = role
        self.maxHealth = self.entity_type.max_health
        self.alive = False
        self.inventory = Inventory()
        self.item_pickup_cooldown = {}
        # log(f'Creating player instance with gamemode: {gamemode}')
        
        if int(gamemode) == Constants.gamemode_enum["creative"]:
            self.inventory.load_preset(0)
        self.health = self.maxHealth

    def tick(self, world):
        """Called every frame to update entity logic/AI."""
        if not self.id:
            raise Exception(f"Cannot tick entity without id, use entity.setID first!")
        
        # if self.ai:
            # self.ai.update(self, world)

        ### PICKUP ITEMS
        for item_entity_id in [item_entity_id for item_entity_id in world.entities if world.entities[item_entity_id].entity_type_id == EntityTypes.ITEM.type_id]:
            item = world.entities[item_entity_id]
            # log(f"Trying to pickup item {item_entity_id} of type {world.entities[item_entity_id].entity_type_id}")
            if self.distance(item) < Constants.Player.pickup_distance:
                if item_entity_id in self.item_pickup_cooldown:
                    if world.current_tick > self.item_pickup_cooldown[item_entity_id]:
                        del self.item_pickup_cooldown[item_entity_id]
                    else:
                        log(f"Preventing item pickup")
                        continue
                log(f"Picking up item!")
                world.removeEntity(item_entity_id)
                self.inventory.pickup_item(Item(item.variation, 1))

    def drop_item(self, drop_stack:bool):
        # item = self.inventory.get_hotbar_slots()
        # TODO
        return

    def move(self, player_movement_request, world):
        if self.y < -500:
            self.die()
        
        if not self.alive:
            log("Error: Cannot move dead player")
            return

        # Apply gravity if not on ground
        if not world.on_ground(self.hitbox):
            self.velocityY += Constants.Player.gravity
        else:
            self.velocityY = 0 

        # Handle jumping
        if player_movement_request.up and world.on_ground(self.hitbox) and not world.hitboxCollide(self.hitbox):
            self.velocityY = Constants.Player.jump_speed

        # Handle horizontal movement
        self.velocityX = 0 
        if player_movement_request.left:
            self.velocityX -= Constants.Player.speed
        if player_movement_request.right:
            self.velocityX += Constants.Player.speed

        old_pos = self.getPos()
        for _ in range(3):
            self.moveBy(self.velocityX, 0)
            if world.hitboxCollide(self.hitbox):
                self.x, self.y = old_pos
                self.velocityX = round(self.velocityX/2, 3)
            else:
                break

        old_pos = self.getPos()
        for _ in range(3):
            self.moveBy(0, self.velocityY)
            if world.hitboxCollide(self.hitbox):
                self.x, self.y = old_pos
                self.velocityY = round(self.velocityY/2, 3)
            else:
                break
        
        self.velocityX = round(self.velocityX, 3)
        self.velocityY = round(self.velocityY, 3)
        self.x = round(self.x, 3)
        self.y = round(self.y, 3)

    def die(self):
        self.alive = False
        if self.server.mode == "local" and self.server.main_player == self.name:
            self.server.show_you_died_screen()

    def respawn(self, world):
        self.velocityX, self.velocityY = 0, 0
        self.x, self.y = world.find_player_world_spawn()
        self.alive = True

    def parse(self) -> str:
        data = json.loads(super().parse())
        data["inventory"] = self.inventory.parse()
        data["gamemode"] = self.gamemode
        return json.dumps(data)

    def load(self, data:str):
        super().load(data)
        parsed_data = json.loads(data)
        try:
            self.gamemode = parsed_data["gamemode"]
        except KeyError:
            self.gamemode = 0
        try:
            self.inventory.load(parsed_data["inventory"])
        except:
            log("Failed to load inventory data.")

class Mob(Entity):
    def __init__(self, x, y, entity_type, currentHealth=None):
        super().__init__(x, y, entity_type)
        self.maxHealth = entity_type.max_health
        self.health = currentHealth if currentHealth is not None else self.maxHealth
        self._savable_attributes.append(["health", int])

class ItemEntity(Entity):
    def __init__(self, x, y, item_stack):
        super().__init__(x, y, EntityTypes.ITEM)
        self.item_stack = item_stack
