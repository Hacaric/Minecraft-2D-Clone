from worldChunk import Chunk, EmptyChunk
from block import Block
from texture_loader import BlockID
from entity import *
from responses import worldRequestTypes, Request
import gameExceptions
import math
import perlin_noise as perlin
import random
import json

class WorldGenerator:
    def __init__(self, chunk_width, chunk_height, seed=None):
        if not seed:
            seed = random.randint(0,999999)
        self.chunk_size_x = chunk_width
        self.chunk_size_y = chunk_height
        self.chunk_size = chunk_width * chunk_height
        self.seed = seed
        self.biomes = json.load(open("biomes.json"))
    def getBiome(self, x):
        return 0
    def generateChunk(self, chunkX):
        def getHeight(worldX):
            return math.sin(worldX/5)*5+32
        # def is_empty(num):
        #     # return num
        #     def normalize(num):
        #         num = num / 2 + 0.5
        #         if num < 0:
        #             num = 0
        #         elif num > 1:
        #             num = 1
        #         return num
        #     # num = normalize(num)
        #     low_ = 0.6
        #     high_ = 12
        #     if num < high_ and num > low_:
        #         return 1
        #     # elif num < 0.1:
        #     #     return 0.5
        #     return 0
        blocks = []
        for x in range(self.chunk_size_x):
            surface_height = math.floor(getHeight(x))
            row = []
            for y in range(self.chunk_size_y):
                if y > surface_height:
                    block = BlockID.AIR
                elif y == 0:
                    block = BlockID.BEDROCK
                else:
                    #CAVES
                    zoom = 0.3
                    d1 = 15*zoom
                    d2 = 40*zoom
                    n1 = perlin.get(x/d1, y/d1, seed=self.seed)
                    n2 = perlin.get(x/d2, y/d2, seed=self.seed+1)
                    value = (n1*0.6 + n2*0.4)
                    if value > 0.6:
                        block = BlockID.AIR
                    else:
                        if y == surface_height and value > 0.4:
                            block = BlockID.GRASS
                        elif y > surface_height - 3 and value > 0.2:
                            block = BlockID.DIRT
                        else:
                            block = BlockID.STONE
                row.append(block)
            blocks.append(row)

        return Chunk(self.chunk_size_x, self.chunk_size_y, blocks)
        # return blocks
    
def test():
    import matplotlib.pyplot as plt
    import numpy as np
    sizeX, sizeY = 64, 64
    generator = WorldGenerator(sizeX, sizeY, seed=random.randint(0, 100000))  # Increased chunk size to 32x32
    chunk = generator.generateChunk(0).blocks

    # Convert chunk blocks into a 2D array for visualization
    chunk_array = np.array(chunk).reshape(generator.chunk_size_x, generator.chunk_size_y)

    plt.figure(figsize=(sizeX, sizeY))  # Set the figure size to display more clearly
    plt.imshow(chunk_array, cmap="terrain", origin="lower")
    plt.colorbar(label="Block Type")
    plt.title("Generated Chunk Visualization")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()
if __name__ == "__main__":
    test()