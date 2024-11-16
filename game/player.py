import pygame
import math
from world_render import get_screen_pos, block_size
class Point2d:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
class defaultPlayer:
    def isnegative(self, x):
        if x < 0:
            return -1
        return 1
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

    
        # Render head
        #screen.blit(pygame.transform.rotate(self.player_textures[t], self.angle), (self.x, self.y - self.sizey / 4))  # Adjust Y position to place head above body
    def __init__(self, x:float, y:float, gamemode:int, sizex:float, sizey:float, angle:float=0)->None:
        self.gamemode = gamemode
        self.health = 20
        self.spawnx = x
        self.spawny = y
        self.x = self.spawnx
        self.y = self.spawny
        self.sizex = sizex - 0.1
        self.sizey = sizey - 0.1
        self.lastfree =   Point2d(self.spawnx, self.spawny)
        self.colour = "#000fff"
        # from texture_storage import player_textures_files, load_player_textures
        # self.player_textures = load_player_textures(player_textures_files)
        #self.block_size = block_size
        self.x_change = 0
        self.y_change = 0
        self.angle = angle
    
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
def text():
    player = defaultPlayer()