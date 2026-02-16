from gameLogger import log
from worldChunk import Chunk, EmptyChunk, ChunkLoadFromStr
from block import Block
from entity import *
from responses import worldRequestTypes, Request
import gameExceptions
import math
from texture_loader import not_full_blocks
from world_generator import WorldGenerator
from entity import Player
from _config import Constants
import queue
import threading
import json


class World:
    def __init__(self, chunk_size_x, chunk_size_y, generator:WorldGenerator=None, seed = None):
        if generator is None:
            generator = WorldGenerator(chunk_size_x, chunk_size_y, seed=seed)
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        # self._chunks_a = {}
        # self._chunks_b = {}
        self.chunks:dict[int, Chunk] = {}
        self.entities:list[Entity] = []
        self.players:list[Player] = []
        self.spawn_chunk:int = None
        self.generator = generator
        self.chunk_gen_queue = queue.Queue(-1)
        self.chunk_gen_threads:dict[int, threading.Thread] = {}
        self.chunk_gen_threads_results:dict[int, any] = {}
        self.chunk_gen_threads_lock:threading.Lock = threading.Lock()
        self.chunk_gen_threads_results_lock_owner:int = None

        self._savable_simple_attributes = [["chunk_size_x", int], ["chunk_size_y", int], ["spawn_chunk", int]]

    def getChunkByIndex(self, x):
        try:
            return self.chunks[x]
        except KeyError:
            # print(f"Error getting chunk {x}: chunk doesnt exist")
            return EmptyChunk(self.chunk_size_x, self.chunk_size_y)
    def getChunkByWorldPos(self, x):
        x = x // self.chunk_size_x
        try:
            return self.chunks[x]
        except KeyError:
            return EmptyChunk(self.chunk_size_x, self.chunk_size_y)
    def addChunk(self, x, chunk):
        self.chunks[x] = chunk
    def removeChunk(self, x):
        try:
            del self.chunks[x]
            return gameExceptions.SUCCESS
        except:
            return gameExceptions.NOT_FOUND
    def getBlock(self, x, y):
        # if 0 <= y < self.chunk_size_y and 0 <= x < self.chunk_size_x:
        #     return 1
        try:
            chunkX = x // self.chunk_size_x
            x = x % self.chunk_size_x
            chunk = self.getChunkByIndex(chunkX)
            return chunk.getBlock(x, y)
        except Exception as e:
            print(f"Error getting block: {e}")
            return gameExceptions.BLOCK_NOT_FOUND
    def getBlocks(self, x1, y1, x2, y2):
        """
        Retuns rectangular part of world.
        @param(float): x1, y1, x2, y2
        @return: list[list[int]]
        - bounds of the rectangle
        - if x1 > x2 error is raised
        - if y1 > y2 error is raised
        - can be floats, x1, y1 is rounded down and x2, y2 is rounded up
        """

        if x1 > x2:
            raise ValueError(f"Error getBlocks - x1 > x2 (x1={x1}, x2={x2})")
        if y1 > y2:
            raise ValueError(f"Error getBlocks - y1 > y2 (y1={y1}, x2={y2})")

        x1, y1 = math.floor(x1), math.floor(y1)
        x2, y2 = math.ceil(x2), math.ceil(y2)
        blocks = []
        for y in range(y1, y2):
            row = []
            for x in range(x1, x2):
                row.append(self.getBlock(x, y))
            # print("ROW", row)
            blocks.append(row)
        # print("BLOCK", blocks, x1, y1, x2, y2)
        return blocks
    def hitboxCollide(self, hitbox:Hitbox):
        blocks = self.getBlocks(hitbox.x, hitbox.y, hitbox.x + hitbox.width, hitbox.y + hitbox.height)
        # print(len(blocks), blocks)
        for row in blocks:
            for block in row:
                if not not_full_blocks[block]:
                    return True
        return False
    def on_ground(self, hitbox:Hitbox):
        return (not self.hitboxCollide(hitbox)) and self.hitboxCollide(Hitbox(hitbox.x, hitbox.y - 0.05, hitbox.width, hitbox.height))
    def generateChunk(self, x, overwrite=False):
        if (x in self.chunks) and (not overwrite):
            return
        else:
            self.chunks[x] = self.generator.generateChunk(x)

    def setBlock(self, x, y, block_type):
        chunkX = x // self.chunk_size_x
        x = x % self.chunk_size_x

        self.chunks[chunkX].setBlock(x, y, block_type)

    def getParsedChunk(self, x) -> tuple[list[int], list[Entity]]:
        """
        Returns chunk data and entities in chunk.
        """
        chunk:Chunk = self.getChunkByIndex(x)
        return chunk.getParsedBlockMap(), chunk.getParsedEntities()
    def find_player_world_spawn(self):
        if self.spawn_chunk is None:
            self.spawn_chunk = sorted(self.chunks.keys(), key=lambda x: abs(x))[0]
        for x in range(self.chunk_size_x):
            collumn = self.chunks[self.spawn_chunk].blocks[x]
            for y in range(self.chunk_size_y-1,-1,-1):
                if not not_full_blocks[collumn[y]]:
                    y += 1
                    return x, y
        return 0, self.chunk_size_y
    def addPlayer(self, player:Player):
        self.players.append(player)
        if self.chunks:
            player.hitbox.x, player.hitbox.y = self.find_player_world_spawn()
    def removePlayer(self, player:Player):
        self.players.remove(player)
    
    def chunkGenThreadFunction(self, chunkX):
        chunk = self.generator.generateChunk(chunkX)
        with self.chunk_gen_threads_lock:
            self.chunk_gen_threads_results_lock_owner = chunkX
            self.chunk_gen_threads_results[chunkX] = chunk
        return

    def tick(self):

        with self.chunk_gen_threads_lock:
            for player in self.players:
                chunkX = player.hitbox.x // self.chunk_size_x
                if (not chunkX in self.chunks) and (not chunkX in self.chunk_gen_threads) and (not chunkX in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX)
                if (not chunkX+1 in self.chunks) and (not chunkX+1 in self.chunk_gen_threads) and (not chunkX+1 in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX+1)
                if (not chunkX-1 in self.chunks) and (not chunkX-1 in self.chunk_gen_threads) and (not chunkX-1 in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX-1)

            while (not self.chunk_gen_queue.empty()) and len(self.chunk_gen_threads.keys()) <= Constants.World.MaxGenerationThreads:
                chunk_x = int(self.chunk_gen_queue.get())
                self.chunk_gen_threads[chunk_x] = threading.Thread(target=self.chunkGenThreadFunction, args=(chunk_x,))
                self.chunk_gen_threads[chunk_x].start()

            keys = list(self.chunk_gen_threads_results.keys())
            for key in keys:
                self.chunks[key] = self.chunk_gen_threads_results[key]
                del self.chunk_gen_threads_results[key]
                del self.chunk_gen_threads[key]

    def parse(self) -> dict:
        data = {}
        # data["chunk_size_x"] = self.chunk_size_x
        # data["chunk_size_y"] = self.chunk_size_y
        for attribute in self._savable_simple_attributes:
            data[attribute[0]] = getattr(self, attribute[0])

        players = []
        for player in self.players:
            players.append(player.parse())
        players = json.dumps(players)
        data["players"] = players

        chunks = {}
        for key, value in self.chunks.items():
            chunks[key] = value.parse()
            print(f"Chunk {key} parsed successfully!")
        chunks = json.dumps(chunks, separators=(",", ":"))
        data["chunks"] = chunks
        # print(f"World's chnks: {self.chunks.keys()}")

        return data
    
    def loadFromDict(self, server, data:dict[str, str], overwrite_loaded_chunks=True)->None:
        players = json.loads(data["players"])
        print("World.loadFromDict: data['players']=", players)
        for player_data in players:
            player = Player(server, "")
            player.load(player_data)
            self.addPlayer(player)
        print(f"World's players: {[player.name for player in self.players]}")

        chunks = json.loads(data["chunks"])
        # print("World.loadFromDict: data['chuks']=", chunks)
        for key, player_data in chunks.items():
            key = int(key)
            if overwrite_loaded_chunks or (not key in self.chunks):
                self.chunks[key] = ChunkLoadFromStr(player_data)
            print(f"Chunk {key} parsed successfully!")


        for attribute in self._savable_simple_attributes:
            try:
                setattr(self, attribute[0], attribute[1](data[attribute[0]]))
            #                               ^^^^ type conversion ^^^^ attribute[1] is type, for example int, so attribute[1](...) = int(...)
            except Exception as e:
                print(f"Error loading attribute '{attribute[0]}' of type '{attribute[1]}': {e}")