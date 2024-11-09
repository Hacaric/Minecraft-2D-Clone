import math
import random
from world_render import Point2d
from texture_storage import block_texture_id, not_full
def random_num(seed, a, b):
    random.seed(seed*(a-201)*(b**2+1))
    # print(random.random())
    return random.random()
chunk_size_x = 32
chunk_size_y = 64
ground_level = 22
terrain_height_variance = 6
terrain_block_difference = 0.01
def check_validity()->None:
    if terrain_height_variance + ground_level > chunk_size_y or ground_level-terrain_height_variance<0:
        Exception("Invalid terrain_height_variance: too high (line:11)")
def Yislegal(y):
    return 0 < y < chunk_size_y

class Chunk:
    def __init__(self):
        self.blocks = [[0 for x in range(chunk_size_y)] for y in range(chunk_size_x)]
        self.width = chunk_size_x
        self.height = chunk_size_y
    def get_block(self,x,y):
        if x < 0 or x >= chunk_size_x or y < 0 or y >= chunk_size_y:
            return 0
        return self.blocks[x][y]
    def set_block(self, x, y, id):
        self.blocks[x][y] = id
    def surface(self, x):
        for y in range(self.height-1, -1, -1):
            #print(y, self.get_block(x, y))
            if not not_full[self.get_block(x, y)]:
                return y
        return -1
        raise("somethik's odd with worldgen (line 34 ;) )")

class World:
    def get_height(self, x, seed):  # Added self to method definition
        #num = (perlin.perlin_noise(x, seed))
        num = math.sin(x) + math.cos(x)#perlin.perlin(x,self.seed)*2-1#
        #num = perlin.perlin_noise(0, x, seed)
        #print(num)
        #print("Noise:", num)
        return round(num, 2)
    #
    #   -------------- POPULATION / DECORATIONS PART ------------------
    #
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

    def generate_chunk(self, chunk_x, seed, population = False):
        thischunk = Chunk()

        #
        #  ------------------ TERRAIN PART ----------------
        #
        for x in range(chunk_size_x):
            height = self.get_height((chunk_x*chunk_size_x + x)*terrain_block_difference, seed)*terrain_height_variance + ground_level
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
            thischunk = self.add_population(thischunk, chunk_x, seed)
        return thischunk
    def get_chunk(self, x, population=True):
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
            self.chunkneg.append(self.generate_chunk(-x-1, self.seed, population=population))  # Added seed
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
            self.chunkpoz.append(self.generate_chunk(x, self.seed, population=population))  # Added seed
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
    def find_nearest_free(self, startx, starty):
        return -1
        if not Yislegal(starty):
            return None
        block_list = [[startx,starty]]
        for i in range(max(chunk_size_x, chunk_size_y)):
            for j in range(len(block_list)):
                current_block_list = block_list.copy()
                for j in range(len(current_block_list)):
                    x, y = current_block_list[j]
                    chunk = self.get_chunk(x // chunk_size_x)
                    x_in_chunk = x % chunk_size_x
                    # Check above
                    if chunk.block(x_in_chunk, y + 1) in not_full:
                        return Point2d(x, y + 1)
                    # Check below
                    if chunk.block(x_in_chunk, y - 1) in not_full:
                        return Point2d(x, y - 1)
                    # Check right
                    if chunk.block((x_in_chunk + 1) % chunk_size_x, y) in not_full:
                        return Point2d(x + 1, y)
                    # Check left
                    if chunk.block((x_in_chunk - 1) % chunk_size_x, y) in not_full:
                        return Point2d(x - 1, y)

                    # Add sides to block_list if not already present
                    if [x, y + 1] not in block_list:
                        block_list.append([x, y + 1])
                    if [x, y - 1] not in block_list:
                        block_list.append([x, y - 1])
                    if [x + 1, y] not in block_list:
                        block_list.append([x + 1, y])
                    if [x - 1, y] not in block_list:
                        block_list.append([x - 1, y])
    # def check_preloaded(self, current_chunkX, playerx):
    #     if playerx // 16 != current_chunkX:
    #         preloadedbaseX = current_chunkX - chunk_size_x
    #         chunkX = playerx // 16
    #         if chunkX + 1 == current_chunkX:
    #             preloaded_area = [self.get_chunk(chunk_size_x * (chunkX - 1))] + preloaded_area[1:3]
    #         elif chunkX + 1 == current_chunkX:
    #             preloaded_area = preloaded_area[0:2] + [self.get_chunk(chunk_size_x * (chunkX + 1))]
    #         else:
    #             preloaded_area = [self.get_chunk(chunk_size_x * (chunkX - 1)), self.get_chunk(chunk_size_x * chunkX), self.get_chunk(chunk_size_x * (chunkX + 1))]

    def __init__(self):
        self.respawn_anchor = None
        self.seed = random.randint(0, 99999999)
        self.chunkpoz = []
        self.chunkneg = []
        self.chunkpoz.append(self.generate_chunk(0, self.seed, population=True))  # Generate the first chunk
        self.background = "#ccd8ff"
        self.block_sound_delay = 7
        self.current_delay = self.block_sound_delay
        self.world_spawn = Point2d(0, self.chunkpoz[0].surface(0)+1)
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
