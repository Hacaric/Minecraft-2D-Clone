import gameExceptions
from gameLogger import log
from entity import Entity
import json

class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Chunk:
    def __init__(self, sizeX, sizeY, blocks:list[list[int]], biome:int = 0):
        self.blocks:list[list[int]] = blocks
        self.biome:int = biome
        self.width = sizeX
        self.height = sizeY
        if not self.validateBlocks(self.blocks, self.width, self.height):
            print(f"Blocks doesn't fit: list size: {len(self.blocks[0])}, {len(self.blocks)}, excepted size: {self.width}, {self.height}.")
            raise Exception(f"Blocks doesn't fit: list size: {len(self.blocks[0])}, {len(self.blocks)}, excepted size: {self.width}, {self.height}.")
            # self.blocks = self.getRectanglePart(0,0,self.width,self.height)
    def validateBlocks(self, blocks, width, height):
        return (
            len(blocks[0]) == height and
            len(blocks) == width
        )
    def validateCoords(self, **values):
        tests = []
        for key in values.keys():
            if key[0] == "x":
                tests.append(0 <= values[key] < self.width)
            elif key[0] == "y":
                tests.append(0 <= values[key] < self.height)
        return not (False in tests)
    def getBlock(self, x:int, y:int):
        if x < self.width and x >= 0 and y < self.height and y >= 0:
            return self.blocks[x][y]
        return -1
    def setBlock(self, x:int, y:int, block_type):
        if x < self.width and x >= 0 and y < self.height and y >= 0:
            self.blocks[x][y] = block_type
        else:
            raise Exception(f"Out of range (Chunk.setBlock) xy: {x}, {y}")
    # def loadData(self, data:list[list[int]], biome:int=None):
    #     self.blocks = data
    #     if not biome is None:
    #         self.biome = biome
    def getColumn(self, x:int, fromY:int, toY:int, disableFill:bool = False): #fromY, toY included
        """
        Gives selected part of blocks in column.

        Args:
            x (int): Column in self.blocks.
            fromY (int): Start of selection from column (included).
            toY (int): End of selecton from column (included).
            disableFill (bool): If False, inexisting items are filled with fill-
            
        Note:
            Fills not existing blaces with 0 if fill enabled (disableFill = False)
        """
        fromY, toY = min(fromY, toY), max(fromY, toY)
        if (toY >= len(self.blocks[0]) or fromY < 0) and not disableFill:
            print("getColumn:debug", x, fromY, toY)
            return ([0 for _ in range(-fromY-1)] + 
                    self.blocks[x][max(fromY, 0):min(toY, len(self.blocks[0]))] + 
                    [0 for _ in range((toY+1) - len(self.blocks[0]))])
        return self.blocks[x][fromY:toY]
    def getRegion(self, fromX:int, fromY:int, toX:int, toY:int) -> list[list[int]]:
        if self.validateCoords(x=fromX, x2=toX, y=fromY, y2=toY):
            leftBottom = XY(min(fromX, toX), min(fromY, toY))
            rightTop = XY(max(fromX, toX), max(fromY, toY))
            section = []
            for x in range(leftBottom.x, rightTop.x):
                section.append(self.blocks[x][leftBottom.y:rightTop.y])
            return section
        else:
            fromX = max(0, min(fromX, self.width))
            toX = max(0, min(toX, self.width))
            fromY = max(0, min(fromY, self.height))
            toY = max(0, min(toY, self.height))
            return self.getRegion(fromX, toX, fromY, toY)
    # def loadData(self, data:list[int], offset:int = 0):
        # """
        # Loads data to chunk.

        # Args:
        #     data (list[list[int]]): Data to load.
        #     offset (int): Offset in data.
        # """
        # if len(data)+offset > self.width * self.height:
        #     print("Warning: Chunk data is too long. Data will be cut.")
        # for i in range(self.width):
        #     for j in range(self.height):
        #         if offset + i * self.width + j < len(data):
        #             self.blocks[i][j] = data[offset + i * self.width + j]
        #         else:
        #             break
    def getParsedEntities(self) -> list[Entity]:
        """
        Returns parsed entities in chunk.
        """
        return []
    def getParsedBlockMap(self) -> list[int]:
        """
        Returns parsed block map.
        """
        block_map = []
        for x in range(self.width):
            for y in range(self.height):
                block_map.append(self.blocks[x][y])
        return block_map
    def parse(self) -> str:
        data = {}
        data["biome"] = self.biome
        data["width"] = self.width
        data["height"] = self.height
        blockdata = self.getParsedBlockMap()
        blockdata = "".join([chr(i) for i in blockdata])
        data["blocks"] = blockdata
        return json.dumps(data, separators=(",", ":"))
    
    def loadFromString(self, data:str)->None:
        # print("Loading chunk data from string", data)
        data = json.loads(data)
        self.biome = data["biome"]
        self.width = data["width"]
        self.height = data["height"]
        # Decode blocks back to list[int]
        self.blocks_raw = [ord(c) for c in data["blocks"]]
        if len(self.blocks_raw) != self.width * self.height:
            log(f"Error loading chunk (Chunk.loadFromString() or ChunkLoadFromStr.__init__()): Not enough block to fill chunk:\nlen(self.blocks_raw) < self.width * self.height => {len(self.blocks_raw)} < {self.width} * {self.height}\nFilling {self.width * self.height - len(self.blocks_raw)} blocks with 0s.")
            self.blocks_raw += [0] * (self.width * self.height - len(self.blocks_raw))
        self.blocks = []
        for x in range(self.width):
            self.blocks.append([])
            for y in range(self.height):
                self.blocks[x].append(self.blocks_raw[x*self.height + y])

class ChunkLoadFromStr(Chunk):
    """
    Regular chunk, but initializer takes chunk data in string and loads them using Chunk.loadFromString()
    """
    def __init__(self, data:str):
        self.loadFromString(data)

class EmptyChunk(Chunk):
    def __init__(self, sizeX, sizeY):
        super().__init__(sizeX, sizeY, [[gameExceptions.BLOCK_NOT_FOUND for _ in range(sizeY)] for _ in range(sizeX)])
    def getParsedBlockMap(self):
        return [0 for _ in range(self.width * self.height)]
# class ListDict:
#     def __init__(self):
#         self.keys = []
#         self.values = []
#     def hash_key(self, key):
#         #print("hash key ", f"{str(type(key))}:{str(key)}")
#         return f"{str(type(key))}:{str(key)}"
#     def add(self, key, value):
#         idx = self.index(key)
#         if idx != -1:
#             self.values[idx].append(value)
#         else:
#             self.keys.append(self.hash_key(key))
#             self.values.append([value])
#         return idx
#     def index(self, key):
#         key = self.hash_key(key)
#         try:
#             return self.keys.index(key)
#         except ValueError:
#             return -1
#     def indexByHashedKey(self, key):
#         try:
#             return self.keys.index(key)
#         except ValueError:
#             return -1
#     def remove(self, key):
#         idx = self.index(key)
#         if idx != -1:
#             self.keys.pop(idx)
#             self.hashed_keys.pop(idx)
#             return self.values.pop(idx)
#         return None
#     def get(self, key):
#         #print("Debug:ListDict.get", key)
#         idx = self.index(key)
#         if idx != -1:
#             return self.values[idx]
#         else:
#             return None
#     def getByHashedKey(self, key):
#         #print("Debug:ListDict.get", key)
#         idx = self.indexByHashedKey(key)
#         if idx != -1:
#             return self.values[idx]
#         else:
#             return None
        
# def compressChunk(blockmap:list[list[int]]):
#     text = "".join(["".join([str(blockmap[i][j]) for j in range(len(blockmap[0]))]) for i in range(len(blockmap))])
#     print(text)
#     MAX_CYCLES = 256
#     compressions:list[ListDict] = []
#     cycle_compression_score = []
#     for cycle in range(MAX_CYCLES):
#         selection_lenght = cycle+1
#         #print("cycle:",cycle)
#         compressions.append(ListDict())
#         for i in range(len(text) - selection_lenght + 1):
#             selection = text[i:i+selection_lenght]
#             if len(selection) < selection_lenght:
#                 #print("Warning (in worldChunk.compressChunk): Selection reached out of the text")
#                 break
#             compressions[cycle].add(selection, i)
#         valid_cycle = False
#         score = []
#         values = []
#         i = 0
#         for value in compressions[cycle].values:
#             print("SCORING VALUE", compressions[cycle].keys[i], ":", len(value))
#             score.append(len(value))
#             values.append(value)
#             if len(value) > 1:
#                 valid_cycle = True
#             i+=1
#         cycle_compression_score.append(f"{cycle}:{values[score.index(max(score))]}:{max(score)*cycle-1}")
#         # print("Cycle validity:", valid_cycle, score)
#         if not valid_cycle:
#             compressions.pop(cycle)
#             break
#     print("\n".join(list(map(str, cycle_compression_score))))
#     return compressions
# compressChunk([[0,1,2,0,1,2,4],[0,1,2,0,1,2,3]])