import pygame
import json
from _config import Constants
from inventory import *
def convert_to_type(object, target_type):
    return target_type(object)

class Hitbox:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
class Entity:
    def __init__(self, hitbox, name=None, texture=None):
        self.hitbox = hitbox
        self.name = name
        self.texture = texture
        # Define which attributes to save. We can extend this in subclasses.
        self._savable_attributes = [["name", str]]
        self._savable_hitbox_attributes = [["x", float], ["y", float], ["width", float], ["height", float]]

    def getPos(self):
        return self.hitbox.x, self.hitbox.y

    def moveBy(self, x, y):
        self.hitbox.x += x
        self.hitbox.y += y

    def moveTo(self, x, y):
        self.hitbox.x = x
        self.hitbox.y = y

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
            print(f"Setting hitbox attr {attr[0]} to {parsed_data[attr[0]]}")
        return json.dumps(parsed_data)

    def load(self, data:str):
        parsed_data = json.loads(data)
        for attribute in self._savable_attributes:
            if attribute[0] in parsed_data:
                setattr(self, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
        for attribute in self._savable_hitbox_attributes:
            if attribute[0] in parsed_data:
                setattr(self.hitbox, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
                print(f"Loading hitbox attr {attribute[0]}: {parsed_data[attribute[0]]}")
        
        # for key, value in parsed_data.items():
        #     if hasattr(self, key):
        #         setattr(self, key, value)
        #     elif hasattr(self.hitbox, key):
        #         setattr(self.hitbox, key, value)
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
    def __init__(self, server, name, hitbox=None, texture=None, role="user", maxHealth=100, currentHealth=None, gamemode=0): # role: "user" or "admin"
        if hitbox is None:
            hitbox = Hitbox(0, 0, 0.4, 1.8)
        super().__init__(hitbox, name, texture)
        # Add Player-specific attributes to the list of savable attributes
        self.gamemode = int(gamemode)
        self._savable_attributes.extend([["role", str], ["maxHealth", int], ["health", int]])
        self.role = role
        self.maxHealth = maxHealth
        self.server = server
        self.velocityX = 0
        self.velocityY = 0
        self.alive = True
        self.inventory = Inventory()
        print(f'Creating player instance with gamemode: {gamemode}, Constants.gamemode_enum["creative"] = {Constants.gamemode_enum["creative"]}')
        if int(gamemode) == Constants.gamemode_enum["creative"]:
            self.inventory.load_preset(0)
        if currentHealth:
            self.health = currentHealth
        else:
            self.health = maxHealth

    def move(self, player_movement_request):
        # print("PlayerY=", self.hitbox.y)
        if self.hitbox.y < -500:
            self.die()

        # Apply gravity if not on ground
        if not self.server.world.on_ground(self.hitbox):
            self.velocityY += Constants.Player.gravity
        else:
            self.velocityY = 0 # Reset vertical velocity if on ground

        # Handle jumping
        if player_movement_request.up and self.server.world.on_ground(self.hitbox) and not self.server.world.hitboxCollide(self.hitbox):
            self.velocityY = Constants.Player.jump_speed

        # Handle horizontal movement
        self.velocityX = 0 # Reset horizontal velocity each tick
        if player_movement_request.left:
            self.velocityX -= Constants.Player.speed
        if player_movement_request.right:
            self.velocityX += Constants.Player.speed

        old_pos = self.getPos()
        for _ in range(3):
            self.moveBy(self.velocityX, 0)
            if self.server.world.hitboxCollide(self.hitbox):
                self.hitbox.x, self.hitbox.y = old_pos
                self.velocityX = round(self.velocityX/2, 3)
            else:
                break
        # Apply horizontal movement and check for collisions
        old_pos = self.getPos()
        for _ in range(3):
            self.moveBy(0, self.velocityY)
            if self.server.world.hitboxCollide(self.hitbox):
                self.hitbox.x, self.hitbox.y = old_pos
                self.velocityY = round(self.velocityY/2, 3)
            else:
                break
        

        # Apply horizontal movement after vertical collision resolution
        # self.moveBy(self.velocityX, 0)
        # if self.server.world.hitboxCollide(self.hitbox):
        #     self.hitbox.x, self.hitbox.y = old_pos # Revert to position before horizontal move
        #     self.velocityX = 0 # Stop horizontal movement on collision

        # No friction applied here, as velocity is reset each tick for horizontal movement
        self.velocityX = round(self.velocityX, 3)
        self.velocityY = round(self.velocityY, 3)
        self.hitbox.x = round(self.hitbox.x, 3)
        self.hitbox.y = round(self.hitbox.y, 3)
    def die(self):
        self.alive = False
        if self.server.mode == "local" and self.server.main_player == self.name:
            self.server.show_you_died_screen()
    def respawn(self):
            self.velocityX, self.velocityY = 0, 0
            self.hitbox.y, self.hitbox.x = self.server.world.find_player_world_spawn()
            self.alive = True
    def parse(self) -> str:
        parsed_data = {}
        for attr in self._savable_attributes:
            parsed_data[attr[0]] = str(getattr(self, attr[0]))
        for attr in self._savable_hitbox_attributes:
            parsed_data[attr[0]] = str(getattr(self.hitbox, attr[0]))
            print(f"Setting hitbox attr {attr[0]} to {parsed_data[attr[0]]}")
        parsed_data["inventory"] = self.inventory.parse()
        return json.dumps(parsed_data)

    def load(self, data:str):
        parsed_data = json.loads(data)
        for attribute in self._savable_attributes:
            if attribute[0] in parsed_data:
                setattr(self, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
        for attribute in self._savable_hitbox_attributes:
            if attribute[0] in parsed_data:
                setattr(self.hitbox, attribute[0], convert_to_type(parsed_data[attribute[0]], attribute[1]))
                print(f"Loading hitbox attr {attribute[0]}: {parsed_data[attribute[0]]}")
        try:
            self.inventory.load(parsed_data["inventory"])
        except:
            print("Failed to load inventory data.")

class Mob(Entity):
    def __init__(self, hitbox, name, texture=None, maxHealth=100, currentHealth=None):
        super().__init__(hitbox, name, texture)
        if currentHealth:
            self.health = currentHealth
        else:
            self.health = maxHealth
class TestEntity(Mob):
    def __init__(self, hitbox, name=None, texture=None):
        super().__init__(self, hitbox, name=name, texture=texture)