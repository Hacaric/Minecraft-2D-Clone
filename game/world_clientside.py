from worldChunk import Chunk, EmptyChunk
from entity import *
from responses import worldRequestTypes, Request
import gameExceptions
from gameLogger import log

testChunk = Chunk(10,10,[[0,1,2,3,4,5,6,7,8,9] for i in range(10)])
exampleHandler = lambda *x: log("Log:",*x)

class World:
    def __init__(self, sizeX, sizeY, requestHandler, player):
        self.chunks:list[Chunk] = {}
        self.chunk_size_x = sizeX
        self.chunk_size_y = sizeY
        self.requestHandler = requestHandler
        self.player = player
        self.entities:list[Entity] = []
    def getChunk(self, x):
        chunkX = x // self.chunk_size_x
        try:
            return self.chunks[chunkX]
        except KeyError:
            return gameExceptions.NOT_FOUND
    def getBlock(self, x, y):
        if 0 <= y < self.chunk_size_y and 0 <= x < self.chunk_size_x:
            chunkX = x // self.chunk_size_x
            x = x % self.chunk_size_x
            chunk = self.getChunk(chunkX)
            if chunk == gameExceptions.NOT_FOUND:
                self.requestHandler(Request(worldRequestTypes.getChunk, chunkX))
                return gameExceptions.WAITING_FOR_RESPONSE
            return chunk.getBlock(x, y)
        elif 0 <= y < self.chunk_size_y:
            self.requestHandler(Request(worldRequestTypes.getChunk, chunkX))
            return gameExceptions.WAITING_FOR_RESPONSE
        else:
            return gameExceptions.INVALID_BLOCKS_POSITION
    def setBlock(self, x, y, id):
        chunk = self.getChunk(x)
        if chunk == gameExceptions.NOT_FOUND:
            self.requestHandler(Request(worldRequestTypes.getChunk, x // self.chunk_size_x))
            return gameExceptions.WAITING_FOR_RESPONSE
        self.requestHandler(Request(worldRequestTypes.setBlock, x, y, id))
        chunk.set_block(x % self.chunk_size_x, y, id)
    def addChunk(self, x, chunk):
        self.chunks[x] = chunk
    def removeChunk(self, x):
        try:
            del self.chunks[x]
        except:
            return gameExceptions.NOT_FOUND
    def getBlocks(self, x_start, y_start, x_end, y_end):
        x_start, x_end = min(x_start, x_end), max(x_start, x_end)
        y_start, y_end = min(y_start, y_end), max(y_start, y_end)

        chunks_loaded:dict[int:Chunk] = {}
        for chunkX in range(x_start // self.chunk_size_x, x_end // self.chunk_size_x + 1):
            chunks_loaded[chunkX] = self.getChunk(chunkX*self.chunk_size_x)
            if chunks_loaded[chunkX] == gameExceptions.NOT_FOUND:
                self.requestHandler(Request(worldRequestTypes.getChunk, chunkX))
                chunks_loaded[chunkX] = EmptyChunk(self.chunk_size_x, self.chunk_size_y)

        blocks = []
        for x in range(x_start, x_end+1):
            blocks.append(chunks_loaded[x//self.chunk_size_x].getColumn(x%self.chunk_size_x, y_start, y_end))
        return blocks
    def loadData(self, chunkX, chunkY:None, data, offset=0):
        if chunkX not in self.chunks:
            self.chunks[chunkX] = Chunk(self.chunk_size_x, self.chunk_size_y, data)
        else:
            self.chunks[chunkX].loadData(data, offset)