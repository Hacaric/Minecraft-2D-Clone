import pygame
class Point2d:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
class defaultPlayer:
    def death(self):
        self.x = self.spawnx
        self.y = self.spawny
        self.health = 20
    def damage(self, cout):
        self.health -= cout
        if self.health <= 0:
            self.death()
    def corners(self):
        return [[self.x, self.y],[self.x,self.y+self.sizey],[self.x+self.sizex,self.y],[self.x+self.sizex,self.y+self.sizey]]

    def render(self, screen, posx, posy):
        import pygame
        import math

        # Render body
        body_texture = pygame.transform.scale(self.player_textures["body"], (self.block_size*4, self.block_size*4))
        body_rect = body_texture.get_rect(center=(self.x + self.sizex/2, self.y + self.sizey/2))
        screen.blit(body_texture, body_rect)

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate angle between player and mouse
        dx = mouse_x - (self.x + self.sizex / 2)
        dy = mouse_y - (self.y + self.sizey / 2)
        angle = math.atan2(dy, dx) % (2*math.pi)

        # Determine which direction the head should face
        if 0 <= angle <= math.pi:
            head_texture = self.player_textures["head_r"]
        elif math.pi < angle < 2*math.pi:
            head_texture = self.player_textures["head_l"]
        else:
            print("ERROR:", angle)

        # Render head
        screen.blit(pygame.transform.rotate(head_texture, angle), (self.x, self.y - self.sizey / 4))  # Adjust Y position to place head above body
    def __init__(self, world, gamemode, sizex, sizey, player_textures, block_size):
        self.gamemode = gamemode
        self.health = 20
        self.spawnx = world.world_spawn.x
        self.spawny = world.world_spawn.y
        self.x = self.spawnx
        self.y = self.spawny
        self.sizex = sizex - 0.1
        self.sizey = sizey - 0.1
        self.lastfree =   Point2d(self.spawnx, self.spawny)
        self.colour = "#000fff"
        self.player_textures = player_textures
        self.block_size = block_size
        self.x_change = 0
        self.y_change = 0
    
    @property
    def _x(self):
        return(self.x)
    @_x.setter
    def _x(self, value):
        self.x_change = self.x
        self.x = value
    @property
    def _y(self):
        return(self.y)
    @_y.setter
    def _y(self, value):
        self.y_change = self.y
        self.y = value