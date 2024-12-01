import math
import perlin
from player import defaultPlayer
import random
import gameExceptions
import texture_loader
from world_render import Point2d
from texture_loader import block_texture_id, not_full_blocks
from biome import *


def random_num(seed, a, b):
    random.seed(seed*(a-201)*(b**2+1))
    # print(random.random())
    return random.random()
chunk_size_x = 16
chunk_size_y = 64
biomes = [Plains, HillyPlains]

# def check_validity()->None:
#     if terrain_height_variance + ground_level > chunk_size_y or ground_level-terrain_height_variance<0:
#         Exception("Invalid terrain_height_variance: too high (line:11)")
def Yislegal(y):
    return 0 < y < chunk_size_y

class Chunk:
    def __init__(self):
        self.blocks = [[0 for _ in range(chunk_size_y)] for _ in range(chunk_size_x)]
        self.width = chunk_size_x
        self.height = chunk_size_y
        self.biome = None
    def get_block(self,x,y):
        if x < 0 or x >= chunk_size_x or y < 0 or y >= chunk_size_y:
            return 0
        return self.blocks[x][y]
    def set_block(self, x, y, id):
        self.blocks[x][y] = id
    def surface(self, x):
        for y in range(self.height-1, -1, -1):
            #print(y, self.get_block(x, y))
            if not not_full_blocks[self.get_block(x, y)]:
                return y
        return -1
        raise("somethik's odd with worldgen (line 34 ;) )")

class World:
    def get_height(self, x):  # Added self to method definition
        #num = (perlin.perlin_noise(x, seed))
        num = (self.NOISE.get(x)+1)/2
        #num = math.sin(x) + math.cos(x)#perlin.perlin(x,self.seed)*2-1#
        #num = perlin.perlin_noise(0, x, seed)
        #print(num)
        #print("Noise:", num)   
        return round(num, 2)
    def add_population(self, thischunk, chunk_x, seed):
        for i in range(chunk_size_x):
            #print("Trying to add sand :d") 
            surface_y = thischunk.surface(i)
            if thischunk.get_block(i, surface_y)==block_texture_id["grass"] and thischunk.get_block(i, surface_y+1)==block_texture_id["air"] and 0.8 < random_num(seed, i, chunk_x) < 1:
                thischunk.blocks[i][surface_y+1] = block_texture_id["short_grass"]
                #print(i, "short_grass")
            if thischunk.get_block(i, surface_y)==block_texture_id["grass"] and thischunk.get_block(i, surface_y+1)==block_texture_id["air"] and 0.1 < random_num(seed+1, i+1, chunk_x) < 0.25:
                thischunk.blocks[i][surface_y+1] = block_texture_id["flower"]
                #print(i, "flower")
            # try:
            #     pass   
            # except Exception as e:
            #     print("Something's wrong:", e)
            #     pass

        return thischunk
    def generate_chunk(self, chunk_x, population = False):
        thischunk = Chunk()
        thischunk.biome = biomes[math.floor(self.CHUNK_NOISE[0].get(chunk_x) * (len(biomes)))]()
        #
        #  ------------------ TERRAIN PART ----------------
        #
        for x in range(chunk_size_x):
            height = self.get_height((chunk_x*chunk_size_x + x)*thischunk.biome.terrain_block_difference)*(thischunk.biome.terrain_height_variance/2 - thischunk.biome.terrain_height_variance) + thischunk.biome.ground_level
            height = round(height)
            for y in range(height, -1, -1):
                if y == 0:
                    thischunk.blocks[x][y] = block_texture_id["bedrock"]
                elif height - y == 0:
                    try:
                        thischunk.blocks[x][y] = block_texture_id["grass"]
                    except Exception as e:
                        print("Error generating chunk", x, y, "\nError message:", e)
                elif height - y > 0:
                    if height - y > 4:
                        thischunk.blocks[x][y] = block_texture_id["stone"]
                    else:
                        thischunk.blocks[x][y] = block_texture_id["dirt"]
                else:
                    thischunk.blocks[x][y] = block_texture_id["air"]
        if population:
            # self.get_chunk(chunk_x+1,population=False)
            # self.get_chunk(chunk_x-1,population=False)
            thischunk = self.add_population(thischunk, chunk_x, self.seed)
        return thischunk
    def get_chunk(self, x, population=True):
        x = math.floor(x)
        #print(self.chunkneg, self.chunkpoz)
        #print(len(self.chunkneg) + len(self.chunkpoz))
        #x = x // chunk_size_x
        #print("Requesting chunk at x:", x)
        if x < 0:
            #print("NEG")
            x = -x
            x -= 1
            #print("Index", x)
            if x < len(self.chunkneg):
                if self.chunkneg[x] is None:  # Fixed 'is None' comparison
                    self.chunkneg[x] = self.generate_chunk(-x-1, self.seed, population=population)  # Added seed
                return self.chunkneg[x]
            while x + 1 < len(self.chunkneg):
                #print("WHILE", len(self.chunkneg))
                self.chunkneg.append(None)
            self.chunkneg.append(self.generate_chunk(-x-1, population=population))  # Added seed
            return self.chunkneg[x]
        else:
            #print("Index",x)
            if x < len(self.chunkpoz):  # Changed to chunkpoz
                if self.chunkpoz[x] == None:  # Fixed 'is None' comparison
                    self.chunkpoz[x] = self.generate_chunk(x, self.seed, population=population)  # Added seed
                return self.chunkpoz[x]
            while x + 1 < len(self.chunkpoz):
                #print("WHILE", len(self.chunkneg))
                self.chunkpoz.append(None)
            self.chunkpoz.append(self.generate_chunk(x, population=population))  # Added seed
            #print(x, print(self.chunkpoz))
            return self.chunkpoz[x]
    def set_block(self, x, y, id):
        #print(x, y, id)
        #if self.churrent_chunkX + 3*chunk_size_x > x//chunk_size_x > self.churrent_chunkX - 1:
            #self.loaded_chunks[self.churrent_chunkX - (x//chunk_size_x)]
        if Yislegal(y):
            chunkX = x // chunk_size_x
            x = x % chunk_size_x
            self.get_chunk(chunkX).set_block(x, y, id)

        # if x < 0:
        #     self.chunkneg[abs(x // chunk_size_x) - 1].blocks[x%chunk_size_x][y] = id
        # else:
        #     self.chunkneg[x // chunk_size_x].blocks[x%chunk_size_x][y] = id
    def get_block(self, x, y):
        chunkX = x // chunk_size_x
        x = x % chunk_size_x
        #print(x, y, self.get_chunk(chunkX).block(x, y))
        return self.get_chunk(chunkX).get_block(x, y)
    def find_player(self, name):
        try:
            return self.nickanmes.index(name)
        except:
            raise gameExceptions.PlayerNotExist()
    def add_player(self, name, x, y, angle):
        if name in self.nicknames:
            raise gameExceptions.PlayerAlreadyExcist()
        self.nickanmes.append(name)
        self.players.append(defaultPlayer(x, y, angle))
    def remove_player(self, name:str):
        index = self.find_player(name)
        self.nickanmes.pop(index)
        self.players.pop(index)
    def __init__(self, not_pregen = False, gamemode=0):
        self.respawn_anchor = None
        self.seed = random.randint(0, 99999999)
        self.NOISE = perlin.PerlinNoise(self.seed, frequency=10)   
        self.CHUNK_NOISE = [perlin.PerlinNoise(self.seed, frequency=0.5, range_=[0,1]), perlin.PerlinNoise(self.seed+2, frequency=1, range_=[0,1])]
        self.chunkpoz = []
        self.chunkneg = []
        if not not_pregen:
            self.chunkpoz.append(self.generate_chunk(0, population=True))
            self.world_spawn = Point2d(0, self.chunkpoz[0].surface(0)+1)
        else:
            self.world_spawn = Point2d(0, 0)
        self.background = "#ccd8ff"
        self.block_sound_delay = 7
        self.current_delay = self.block_sound_delay
        self.active = []
        self.player_sizex = 0.3
        self.player_sizey = 1.8
        self.gamemode = gamemode #0 - creative, 1 - survival
        self.getblock = self.get_block #Beeacouse im forgitting to write the "_" :D
        #player = defaultPlayer(overworld, 0, player_sizex, player_sizey, player_textures, block_size)
        self.main_player = defaultPlayer(self.world_spawn.x, self.world_spawn.y, 0, self.player_sizex, self.player_sizey)
        self.player_color = (0, 20, 255)  # Gray color
        self.players = []#, defaultPlayer(self, 0, self.player_sizex, self.player_sizey)]
        self.nicknames = []
        #self.test_player = defaultPlayer(self, 0, self.player_sizex, self.player_sizey, texture_storage.load_player_textures())
        # self.churrent_chunkX = 0
        # self.loadedbaseX = -chunk_size_x
        # self.loaded_chunks = [self.get_chunk(-1), self.get_chunk(0), self.get_chunk(1)]
# myworld = World()
# print(myworld.chunkpoz[0].blocks)
# for x in range(chunk_size_x):
#     for y in range(chunk_size_y):
#         print(myworld.block(x, y), end = "")
#     print()
def test():
    print("\n\ntest")
    my = World()
