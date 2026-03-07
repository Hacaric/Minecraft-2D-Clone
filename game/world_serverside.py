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
import time
import uuid


class World:
    def __init__(self, chunk_size_x, chunk_size_y, generator:WorldGenerator=None, seed = None):
        if generator is None:
            generator = WorldGenerator(chunk_size_x, chunk_size_y, seed=seed)
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        # self._chunks_a = {}
        # self._chunks_b = {}
        self.chunks:dict[int, Chunk] = {}
        self.entities:dict[str, Entity] = {}
        # self.entity_id_map:dict[str, Entity] = {}
        self.players:dict[str, Player] = {}
        self.spawn_chunk:int = None
        self.generator = generator
        self.chunk_gen_queue = queue.Queue(-1)
        self.chunk_gen_threads:dict[int, threading.Thread] = {}
        self.chunk_gen_threads_results:dict[int, any] = {}
        self.chunk_gen_threads_lock:threading.Lock = threading.Lock()
        self.chunk_gen_threads_results_lock_owner:int = None
        self.blocks_getting_broken = {}
        self.current_tick = 0
        self.block_breaking_delay_ticks = 50
        self.doBlockDrops = True # TODO: Add gamerules

        self._savable_simple_attributes = [["chunk_size_x", int], ["chunk_size_y", int], ["spawn_chunk", int]]

    def getChunkByIndex(self, x):
        try:
            return self.chunks[x]
        except KeyError:
            # log(f"Error getting chunk {x}: chunk doesnt exist")
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
            log(f"Error getting block: {e}")
            return Block(gameExceptions.BLOCK_NOT_FOUND)
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
            # log("ROW", row)
            blocks.append(row)
        # log("BLOCK", blocks, x1, y1, x2, y2)
        return blocks
    def hitboxCollide(self, hitbox:Hitbox):
        blocks = self.getBlocks(hitbox.x, hitbox.y, hitbox.x + hitbox.width, hitbox.y + hitbox.height)
        # log(len(blocks), blocks)
        for row in blocks:
            for block in row:
                if not not_full_blocks[block.id]:
                    return True
        return False
    def on_ground(self, hitbox:Hitbox):
        return (not self.hitboxCollide(hitbox)) and self.hitboxCollide(Hitbox(hitbox.x, hitbox.y - 0.05, hitbox.width, hitbox.height))
    def generateChunk(self, x, overwrite=False):
        if (x in self.chunks) and (not overwrite):
            return
        else:
            self.chunks[x] = self.generator.generateChunk(x)

    def setBlock(self, x, y, block):
        chunkX = x // self.chunk_size_x
        x = x % self.chunk_size_x

        if isinstance(block, int):
            block = Block(block)
        log(f"Setting block {x}, {y} to {block} of id {block.id}")
        self.chunks[chunkX].setBlock(x, y, block)
    def changeBreakingProgress(self, x, y, progress_change):
        self.blocks_getting_broken[(x,y)] = self.current_tick
        try:
            chunkX = x // self.chunk_size_x
            chunk_relative_x = x % self.chunk_size_x
            # log(f"Affecting block on {x} {y}")
            chunk = self.getChunkByIndex(chunkX)
            block = chunk.getBlock(chunk_relative_x, y)
            if isinstance(block, int):
                log(f"WARNING: Some blocks are stored as integers instead of Block instance: x:{x}, y:{y}, value:{block}")
                block = Block(block)
            current_breaking_progress = block.breaking_progress
            block_hardness = 5
            if current_breaking_progress + progress_change >= block_hardness:
                chunk.setBlock(chunk_relative_x, y, 0)
                del self.blocks_getting_broken[(x,y)]
                # return block
                if self.doBlockDrops:
                    self.addEntity(Entity(x, y, EntityTypes.ITEM, variation=block.id))
            else:
                chunk.getBlock(chunk_relative_x, y).breaking_progress += progress_change
            return None
        except Exception as e:
            log(f"Error changing breaking progress: {e}")
            return gameExceptions.INVALID_BLOCK
        
    def setBreakingProgress(self, x, y, progress_value):
        self.blocks_getting_broken[(x,y)] = self.current_tick
        try:
            chunkX = x // self.chunk_size_x
            chunk_relative_x = x % self.chunk_size_x
            # log(f"Affecting block on {x} {y}")
            chunk = self.getChunkByIndex(chunkX)
            block = chunk.getBlock(chunk_relative_x, y)
            if isinstance(block, int):
                log(f"WARNING: Some blocks are stored as integers instead of Block instance: x:{x}, y:{y}, value:{block}")
                block = Block(block)
            block_hardness = 5
            if progress_value >= block_hardness:
                chunk.setBlock(chunk_relative_x, y, 0)
                del self.blocks_getting_broken[(x,y)]
                return block
            else:
                chunk.getBlock(chunk_relative_x, y).breaking_progress = progress_value
                return None
        except Exception as e:
            log(f"Error setting breaking progress: {e}")
            return gameExceptions.INVALID_BLOCK
        # try:
        #     chunkX = x // self.chunk_size_x
        #     x = x % self.chunk_size_x
        #     chunk = self.getChunkByIndex(chunkX)
        #     block = chunk.getBlock(x, y)
        #     if isinstance(block, int):
        #         log(f"WARNING: Some blocks are stored as integers instead of Block instance: x:{x}, y:{y}, value:{block}")
        #         block = Block(block)
        #     block_hardness = 5
        #     if progress_value >= block_hardness:
        #         self.setBlock(x, y, 0)
        #         return block
        #     else:
        #         chunk.getBlock(x, y).breaking_progress = progress_value
        #         return None
        # except Exception as e:
        #     log(f"Error setting breking progress: {e}")
        #     return gameExceptions.BLOCK_NOT_FOUND


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
                if not not_full_blocks[collumn[y].id]:
                    y += 1
                    return x, y
        return 0, self.chunk_size_y
    def addPlayer(self, player:Player, force=False) -> str|None:
        """Adds player to the world and returns it's id (usually name) or None on fail"""
        log(f"Adding player {player.name}")
        player_id = str(player.name)
        if player_id in self.players and not force:
            log(f"Error adding player: player is already connected, refusing connection.")
            return None
        self.players[player_id] = player
        if self.chunks and not player.alive:
            player.respawn(self)
        self.addEntity(player, id=player_id)
        return player.name
    def removePlayer(self, player_id:str):
        self.players[player_id].id = None # Disable any remaining functionality
        del self.players[player_id]
    
    def chunkGenThreadFunction(self, chunkX):
        chunk = self.generator.generateChunk(chunkX)
        with self.chunk_gen_threads_lock:
            self.chunk_gen_threads_results_lock_owner = chunkX
            self.chunk_gen_threads_results[chunkX] = chunk
        return
    
    def getUniqueEntityID(self):
        id = uuid.uuid4().hex
        while id in self.entities:
           id = uuid.uuid4().hex
        return id 
    
    def addEntity(self, entity:Entity, id=None):
        log(f"Adding entity: type: '{entity.entity_type_id}', id: '{id}'")
        if not id:
            id = self.getUniqueEntityID()
        entity.setID(id, self.current_tick)
        self.entities[id] = entity

    def removeEntity(self, entity_id):
        self.entities[entity_id].setID(None, self.current_tick)
        del self.entities[entity_id]

    def spawn_entities(self):
        return
        # if self.current_tick == 0:
        #     # Test item
        #     self.addEntity(Entity(0, 50, EntityTypes.ITEM, variation=3))

    def tick_func(self):
        with self.chunk_gen_threads_lock:
            # Chunk generation - using threads - the earlier it starts the better
            while (not self.chunk_gen_queue.empty()) and len(self.chunk_gen_threads.keys()) <= Constants.World.MaxGenerationThreads:
                chunk_x = int(self.chunk_gen_queue.get())
                self.chunk_gen_threads[chunk_x] = threading.Thread(target=self.chunkGenThreadFunction, args=(chunk_x,))
                self.chunk_gen_threads[chunk_x].start()
            keys = list(self.chunk_gen_threads_results.keys())
            for key in keys:
                self.chunks[key] = self.chunk_gen_threads_results[key]
                del self.chunk_gen_threads_results[key]
                del self.chunk_gen_threads[key]

            # Players
            for player in self.players.values():
                chunkX = player.hitbox.x // self.chunk_size_x
                if (not chunkX in self.chunks) and (not chunkX in self.chunk_gen_threads) and (not chunkX in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX)
                if (not chunkX+1 in self.chunks) and (not chunkX+1 in self.chunk_gen_threads) and (not chunkX+1 in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX+1)
                if (not chunkX-1 in self.chunks) and (not chunkX-1 in self.chunk_gen_threads) and (not chunkX-1 in self.chunk_gen_threads_results):
                    self.chunk_gen_queue.put(chunkX-1)

            # Entities
            self.spawn_entities()
            # log("Entity list: ", [i.entity_type_id for i in self.entities.values()])
            for entity_id in list(self.entities.keys()):
                if entity_id in self.entities: # Prevent deleted entities from being processed (like picked up items)
                    entity = self.entities[entity_id]
                    entity.tick(self)
                    # if entity.entity_type_id == EntityTypes.PLAYER.type_id:
                    #     log(entity.debug_info(self))
                    
            # Reset block breaking progress
            for key in self.blocks_getting_broken:
                if self.current_tick - self.blocks_getting_broken[key] > self.block_breaking_delay_ticks:
                    self.setBreakingProgress(key[0], key[1], 0)
        self.current_tick += 1

    def parse(self) -> dict:
        data = {}
        # data["chunk_size_x"] = self.chunk_size_x
        # data["chunk_size_y"] = self.chunk_size_y
        for attribute in self._savable_simple_attributes:
            data[attribute[0]] = getattr(self, attribute[0])

        # players = []
        # for player in self.players.values():
        #     players.append(player.parse())
        # players = json.dumps(players)
        # data["players"] = players

        chunks = {}
        for key, value in self.chunks.items():
            chunks[key] = value.parse()
            log(f"Chunk {key} parsed successfully!")
        chunks = json.dumps(chunks, separators=(",", ":"))
        data["chunks"] = chunks
        # log(f"World's chnks: {self.chunks.keys()}")

        entities = {}
        for key, value in self.entities.items():
            entities[key] = value.parse()
            log(f"Entity {key} (type:{value.entity_type_id}) parsed successfully!")
        entities = json.dumps(entities)
        log(f"Parsed entities: {entities}")
        data["entities"] = entities

        return data
    
    def loadFromDict(self, server, data:dict[str, str], overwrite_loaded_chunks=True)->None:
        # players = json.loads(data["players"])
        # log("World.loadFromDict - data['players']: ", players)
        # for player_data in players:
        #     player = Player("",0,0)
        #     player.load(player_data)
        #     self.addPlayer(player)
        # log(f"World's players: {self.players.keys()}")

        chunks = json.loads(data["chunks"])
        # log("World.loadFromDict: data['chuks']=", chunks)
        for key, chunk_data in chunks.items():
            key = int(key)
            if overwrite_loaded_chunks or (not key in self.chunks):
                self.chunks[key] = ChunkLoadFromStr(chunk_data)
            log(f"Chunk {key} loaded successfully!")

        entities = json.loads(data["entities"])
        # log("World.loadFromDict: data['chuks']=", chunks)
        for entity_id, entity_data in entities.items():
            # if entity_data["entity_type_id"] == EntityTypes.PLAYER.type_id:
            #     player = Player(entity_id,0,0)
            #     player.load(entity_data)
            #     self.addEntity(player, id=entity_id)
            # else:# entity_data["entity_type_id"] == EntityTypes.ITEM
            entity = LoadEntityFromString(entity_data)
            log("Before:", entity.debug_info(self))
            if entity.entity_type_id == EntityTypes.PLAYER.type_id:
                self.addPlayer(entity)
            else:
                self.addEntity(entity, id=entity_id)
            log("After:", entity.debug_info(self))
            log(f"Entity {entity_id} (type:{self.entities[entity_id].entity_type_id}) loaded successfully!")


        for attribute in self._savable_simple_attributes:
            try:
                setattr(self, attribute[0], attribute[1](data[attribute[0]]))
            #                               ^^^^ type conversion ^^^^ attribute[1] is type, for example int, so attribute[1](...) = int(...)
            except Exception as e:
                log(f"Error loading attribute '{attribute[0]}' of type '{attribute[1]}': {e}")