import pygame
import sys
import menu_tree as gui
from menu_tree import status, action, gui_action
from worldChunk import Chunk, XY
from world_clientside import World as WorldClientSide
from world_serverside import World as WorldServerSide
from world_generator import WorldGenerator
import texture_loader
import threading
import time
import socket_.client as socketModules
import random
# import subprocess
from protocol import *
import os
# from importlib.machinery import SourceFileLoader # importing server.py from path
from gameLogger import *
import math
import json
from entity import Entity, Player, Hitbox, Mob
from _config import ConfigFiles, Constants, Defaults
from keys import keydict
import world_files as world_files


WINDOW_WIDTH, WINDOW_HEIGHT = Constants.Screen.width, Constants.Screen.height
FPS = Constants.Screen.FPS
PYTHON_BASH_COMMAND = "python"
SERVER_FILE_PATH = "./server3.py"
DEFAULT_PORT = random.randint(1111,9999)
LOCALHOST = "127.0.0.1"
SPLIT_CHR = "\x01"
KEYS = keydict.copy()
GAME_DIR = os.path.dirname(__file__)
threads_running = []

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

    CHUNK_SIZE_X, CHUNK_SIZE_Y = Constants.chunk_width, Constants.chunk_height
    block_in_screenX = Constants.Screen.block_in_screenX
    block_size = Constants.Screen.block_size
    block_in_screenY = Constants.Screen.block_in_screenY
    show_f3_screen = True

    cursor_textures, block_textures, sounds, item_textures, player_textures, gui_textures, health_bar_textures = texture_loader.load_all(block_size, 1)
    player_textures["body"] = pygame.transform.scale(player_textures["body"], (Constants.Player.size[0]*block_size, Constants.Player.size[1]*block_size))


    new_log_file(os.path.join(os.path.dirname(__file__), "./log/"), "client-latest.log", replace=True)
    new_log_file(os.path.join(os.path.dirname(__file__), "./log/"), "client.log")

def register_thread(thread):
    global threads_running
    log(f"Registering thread {thread}")
    threads_running.append(thread)
def unregister_thread(thread):
    global threads_running
    log(f"Unregistering thread {thread}")
    threads_running.remove(thread)

class MouseInput:
    def __init__(self):
        self.mouse_click = False
        self.mouse_pos = (0, 0)
        self.events = []
        self.button_states = [False] * 3
    def update(self, mouse_click, events, mouse_pos, button_states:tuple[bool,bool,bool]):
        self.mouse_click = mouse_click
        self.mouse_pos = mouse_pos
        self.events = events
        self.button_states = button_states
    def read(self):
        # Return a tuple of the current state
        currData = (self.mouse_click, self.events, self.mouse_pos, self.button_states)
        # Reset per-frame data
        self.mouse_click = False
        return currData
class Flag:
    def __init__(self, type, *args, **kwargs):
        log("flag ", type, args, kwargs)
        self.type = type
        self.args = args
        self.kwargs = kwargs
class DisplayManager:
    def __init__(self, guiHandler, game, currentState="gui"):
        self.state = currentState
        self.renderer:Renderer = None
        self.game = game
        # self.flags: list[list[str]] = []
        self.guiManager:gui.GuiHandler = guiHandler
        self.flag__take_screenshot = False
        self.pause_menu_background:pygame.Surface = self.guiManager.menu_collection.tree.get("Pause_menu").background
    # def setflag(self, flag, *param):
    #     self.flags.append([flag, *param])

    def tick(self, mouse_down, events, mouse_pos):
        if self.state == "gui":
            response = self.guiManager.tick(mouse_down, events, mouse_pos, KEYS)
            if response == status.terminate:
                global running
                running = False
                log("\nProcess termination requested by user.\nExiting...")
            # elif type(response) == gui_action:
            #     if response.action == "newWorld":
            #         port, ip = self.game.startServer(response)
            #         self.game.connectServer(port, ip)
            #         self.state = "game"
            #     elif response.action == "loadWorld":
            #         port, ip = self.game.startServer(response)
            #         self.game.connectServer(port, ip)
            #         self.state = "game"
        elif self.state == "game":
            if KEYS[pygame.K_ESCAPE]:
                self.guiManager.menu_collection.current_menu_idx = self.guiManager.menu_collection.tree.find("Pause_menu")
                self.state = "game_paused"
                KEYS[pygame.K_ESCAPE] = False
                self.game.ingame = False
                log("Game paused")
                log(self.guiManager.menu_collection.current_menu_idx)
                self.flag__take_screenshot = True

        elif self.state == "game_paused":
            # if KEYS[pygame.K_ESCAPE]:
            #     self.state = "game"
            #     KEYS[pygame.K_ESCAPE] = False
            # screen.blit(self.pause_game_screenshot, (0,0))
            response = self.guiManager.tick(mouse_down, events, mouse_pos, KEYS)
            if response == status.terminate:
                self.state = "game"
                KEYS[pygame.K_ESCAPE] = False
                self.game.ingame = True
                log("Game unpaused")
            elif response == status.signal:
                self.state = "gui"
                self.game.ingame = False
                log("Game left")
                self.guiManager.menu_collection.current_menu_idx = self.guiManager.menu_collection.tree.find("Main")
                log(self.guiManager.menu_collection.current_menu_idx)
                self.game.exitToMenu()

                

    def render(self):
        if self.flag__take_screenshot:
            log("Taking screenshot")
            background = self.renderer.newFrame()
            self.renderer.drawUI(background)
            if show_f3_screen:
                self.renderer.draw_f3_screen(background)
            overlay = pygame.Surface(background.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            background.blit(overlay, (0,0))
            self.pause_menu_background.blit(background, (0,0))
            self.flag__take_screenshot = False

        if self.state == "gui":
            self.guiManager.render(screen)
        elif self.state == "game":
            pass
            # self.renderer.render()
            # self.guiManager.render(screen)
        elif self.state == "game_paused":
            self.guiManager.render(screen)

class StaticCamera:
    def __init__(self, pos:tuple[int, int]=(0,0), size:tuple[int, int]=(WINDOW_WIDTH, WINDOW_HEIGHT)):
        self.position = XY(*pos)
        self.size = XY(*size)
    def getGetCameraBoundBox(self) -> tuple[int, int, int, int]:
        return (self.position.x, self.position.y, self.position.x + self.size.x, self.position.y + self.size.y)
class TrackingCamera:
    def __init__(self, target, offset=(0,0), center_target=1):
        """
        Create camera to target an instance of Entity or any of its subclasses.
        @param target: Entity to track
        @param offset: Offset from target to camera
        @param center_target: 
            - If 1, camera will be centered to target's center
            - If 0, camera will be centered to target's position
            - If -1, camera's position will be set to target's position
        """
        self.target:Entity = target
        self.target_size = self.target.hitbox.width, self.target.hitbox.height
        self.offset = offset
        self.size = WINDOW_WIDTH, WINDOW_HEIGHT
        self.center_target = center_target

        # Setting the function instead of checking every time should speed up rendering!
        if self.center_target == 1:
            self.getGetCameraBoundBox = self._getGetCameraBoundBox_center_target_center
        elif self.center_target == 0:
            self.getGetCameraBoundBox = self._getGetCameraBoundBox_center_target_coodrs
        elif self.center_target == -1:
            self.getGetCameraBoundBox = self._getGetCameraBoundBox_no_center
    # def update(self):
    #     """
    #     IMPORTANT: Don't call this function for entity movement!!!
    #     Entity movement is updated automatically
    #     """

    def _getGetCameraBoundBox_center_target_center(self) -> tuple[int, int, int, int]:
        return (self.target.hitbox.x + self.offset[0] - self.size[0]/block_size/2 + self.target.hitbox.width/2, 
                self.target.hitbox.y + self.offset[1] - self.size[1]/block_size/2 + self.target.hitbox.height/2, 
                self.target.hitbox.x + self.offset[0] + self.size[0]/block_size/2 + self.target.hitbox.width/2, 
                self.target.hitbox.y + self.offset[1] + self.size[1]/block_size/2 + self.target.hitbox.height/2)
    def _getGetCameraBoundBox_center_target_coodrs(self) -> tuple[int, int, int, int]:
        return (self.target.hitbox.x + self.offset[0] - self.size[0]/block_size/2, 
                self.target.hitbox.y + self.offset[1] - self.size[1]/block_size/2, 
                self.target.hitbox.x + self.offset[0] + self.size[0]/block_size/2, 
                self.target.hitbox.y + self.offset[1] + self.size[1]/block_size/2)
    def _getGetCameraBoundBox_no_center(self) -> tuple[int, int, int, int]:
        return (self.target.hitbox.x + self.offset[0], 
                self.target.hitbox.y + self.offset[1], 
                self.target.hitbox.x + self.offset[0] + self.size[0]/block_size, 
                self.target.hitbox.y + self.offset[1] + self.size[1]/block_size)
    def getGetCameraBoundBox(self) -> tuple[int, int, int, int]:
        """
        Generated based on @center_target in __init__ property. Bounds are transformed using offset (tuple[int, int]) and center_target (bool).
        
        IMPORTANT: Pygame (more like me) tents to mess y coordinate, here the bottom is 0, but in pygame 0 it top. I WiLl NoT cHaNgE tHiS! :)
        
        @return: tuple[int, int, int, int]

        Returns bounds for the camera.
        - x coordinate  (Left side) - the smaller one
        - y coordinate  (Bottom side) - the smaller one
        - x coordinate  (Right side) - the bigger one
        - y coordinate  (Top side) - the bigger one
        """
        raise Exception(f"Error: Functon TrackingCamera.getGetScreenProperties called before loaded in __init__.")
def remove_comments(text:list[str], comment_start="//"):
    for i in range(len(text)):
        comment_index = text[i].find(comment_start)
        if comment_index != -1:
            text[i] = text[i][:comment_index]
    return text

def format_number(reference_surface, n1, n2):    
    # log(f"n1: {n1}, n2: {n2} UNFORMATED, {reference_surface.get_size()}")
    try:
        if isinstance(n1, str):
            try:
                n1 = int(n1)
            except:
                if n1[-1] == "%":
                    n1 = int(n1[:-1]) * reference_surface.get_size()[0] / 100
                elif n1[-2:] == "px":
                    n1 = int(n1[:-2])
                elif n1[-2:] == "vw":
                    n1 = int(n1[:-2]) * WINDOW_WIDTH / 100
                elif n1[-2:] == "vh":
                    n1 = int(n1[:-2]) * WINDOW_HEIGHT / 100
    except Exception as e:
        log(f"Error in n1 format_number: {e}")
        n1 = None

    try:
        if isinstance(n2, str):
            try:
                n2 = int(n2)
            except:
                if n2[-1] == "%":
                    n2 = int(n2[:-1]) * reference_surface.get_size()[1] / 100
                elif n2[-2:] == "px":
                    n2 = int(n2[:-2])
                elif n2[-2:] == "vw":
                    n2 = int(n2[:-2]) * WINDOW_WIDTH / 100
                elif n2[-2:] == "vh":
                    n2 = int(n2[:-2]) * WINDOW_HEIGHT / 100
    except Exception as e:
        log(f"Error in n2 format_number: {e}")
        n2 = None
    # log(f"n1: {n1}, n2: {n2}")
    return n1, n2

class GameUIElement:
    def __init__(self, data:dict):
        try:
            texture_path, pos, size = data["texture_path"], data["pos"], data["size"]
        except Exception as e:
            log(f"Error loading UI element: {e}")
        self.input_size = size
        self.input_pos = pos
        self.pos = (None, None)
        self.size = (None, None)
        self.screen_size = (None, None)
        self.texture_path = texture_path
        self.texture = pygame.image.load(texture_path)
        # self.texture = pygame.transform.scale(self.texture, size)

    def render(self, screen):
        if self.screen_size != screen.get_size():
            
            self.size = format_number(screen, *self.input_size)

            self.pos = format_number(screen, *self.input_pos)
            # log("GUI_ELEMENT_RENDER", self.pos, self.size)

            self.texture = pygame.transform.scale(self.texture, self.size)
            
        screen.blit(self.texture, self.pos)

class GameUI:
    def __init__(self,config_file):
        with open(config_file, "r") as f:
            text = f.read()
            text = remove_comments(text.split("\n"))
            text = "\n".join(text)
            self.data = json.loads(text)
        # Data format: dict[list,dict[dict[str,any]]]
        log(f"GAMEUI: {str(self.data)}")
        self.render_elements = self.data["render"]
        self.elements_unresolved = self.data["elements"]
        self.elements = {}
        # self.elements_resolved = {}
        # for key in elements.keys:
        #     for property in elements[key].keys():
        #         self.elements_resolved[key][property] = elements[key][property]
        for key in self.elements_unresolved.keys():
            try:
                self.elements[key] = GameUIElement(self.elements_unresolved[key])
                # for property in self.elements_unresolved[key].keys():
                #     try:
                #         self.elements_unresolved[key][property]
                #     except:
                #         self.elements_unresolved.pop(key)
                #         log(f"Error: {key} is missing property {property}.")
            except Exception as e:
                log(f"Error confguring element '{key}': '{e}'.")
        for key in self.render_elements:
            try:
                self.elements[key]
            except:
                self.render_elements.remove(key)
                log(f"Error: render element {key} doesn't exist")


    def render(self, screen):
        for key in self.render_elements:
            self.elements[key].render(screen)


class Renderer:
    def __init__(self, screen, world, camera, ui_config_file, mouseInput:MouseInput, game):
        # When resizing window delete renderer and create new one
        # self.gameUI = GameUI("./ui.json")
        if screen is None or world is None or camera is None:
            raise ValueError("Renderer: screen, world and camera can't be None")
        self.cursor_world_pos = (0,0)
        self.screen:pygame.Surface = screen
        self.world:WorldServerSide = world
        self.camera:TrackingCamera = camera
        # self.ui:list[str] = ui
        self.ui_text = ["Loading..." for i in range(2)]
        self.ui = GameUI(ui_config_file)
        self.temp_framePrototype = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.original_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.mouseInput = mouseInput
        self.game = game
        if self.temp_framePrototype is None:
            raise ValueError("Renderer: framePrototype is None")
    def newFrame(self):
        if not self.original_size == (WINDOW_WIDTH, WINDOW_HEIGHT):
            log("Resize", color="#FF0080")
            self.original_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
            self.temp_framePrototype = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            self.temp_framePrototype.fill((0,0,0))
        # log(self.camera.getGetCameraBoundBox())
        # log([i//block_size for i in self.camera.getGetCameraBoundBox()])
        camera_bounds = self.camera.getGetCameraBoundBox()
        # log(bounds)
        camera_base_in_world = math.floor(camera_bounds[0]), math.floor(camera_bounds[1])
        camera_bounds = (camera_bounds[0]-1, camera_bounds[1]-1, camera_bounds[2], camera_bounds[3])
        blockmap:list[list[int]] = self.world.getBlocks(*camera_bounds)
        # log(blockmap)
        screen_offset:tuple[float, float] = (math.floor(camera_bounds[0]) - camera_bounds[0] - 1, camera_bounds[1] - math.floor(camera_bounds[1]) - 1)
        self.cursor_world_pos = (math.floor(camera_bounds[0] + self.mouseInput.mouse_pos[0]/block_size + 1), 
                                 math.floor(camera_bounds[3] - self.mouseInput.mouse_pos[1]/block_size))
        # log(self.cursor_world_pos, self.mouseInput.mouse_pos[1]/block_size)
        # try:
        #     self.world.setBlock(*self.cursor_world_pos, -1)
        # except:
        #     pass
        for y in range(len(blockmap)):
            for x in range(len(blockmap[0])):
                # if (camera_base_in_world[0] + x, camera_base_in_world[1] + y) == self.cursor_world_pos:
                #     self.temp_framePrototype.blit(block_textures[-1], ((x+screen_offset[0])*block_size,(y+screen_offset[1])*block_size))
                # else:
                    self.temp_framePrototype.blit(block_textures[blockmap[len(blockmap)-1-y][x]], ((x+screen_offset[0])*block_size,(y+screen_offset[1])*block_size))
        # log(self.world.chunks)
        self.temp_framePrototype.blit(player_textures["body"], (self.temp_framePrototype.get_size()[0]//2 - player_textures["body"].get_size()[0]//2, self.temp_framePrototype.get_size()[1]//2 - player_textures["body"].get_size()[1]//2))
        self.temp_framePrototype.blit(cursor_textures[0], ((self.cursor_world_pos[0] - camera_base_in_world[0] + screen_offset[0] + 1)*block_size, 
                                                           (math.floor(camera_bounds[3]) - self.cursor_world_pos[1] + screen_offset[1])*block_size))
        return self.temp_framePrototype
    def drawUI(self, frame):
        self.ui.render(frame)
    def draw_f3_screen(self, frame):
        self.ui_text[0] = f"X: {self.world.players[0].hitbox.x}, Y: {self.world.players[0].hitbox.y}"
        self.ui_text[1] = f"TPS: {self.game.TPS}"
        font = pygame.font.Font(None, 24)
        for i in range(len(self.ui_text)):
            # log("Rndering ui text", i)
            text_surface = font.render(self.ui_text[i], True, (255, 0, 255))
            frame.blit(text_surface, (5, i*26))
        
    def render(self):
        frame = self.newFrame()
        self.drawUI(frame)
        if show_f3_screen:
            pass
            self.draw_f3_screen(frame)
        self.screen.blit(frame, (0,0))
        # pygame.display.flip()

class Server:
    def __init__(self, mode:str = "online"):
        self.world = None
        self.running = None
        self.world_generator = None
        self.seed = None
        self.mode = mode

class InternalServer:
    def __init__(self):
        self.world = None
        self.running = False
        self.main_player = None
        self.world_generator = None
        self.seed = None
        self.mode = "local"
    def start(self):
        if not self.world:
            raise "Error in InternalServer.start(): world doesn't exist load world before starting!"
        self.running = True
    def new_world(self, name, gamemode, username, seed = None):
        self.main_player = username
        if isinstance(seed, int):
            pass
        elif seed:
            try:
                seed = hash(seed)
            except TypeError:
                log("Unhashable type:", type(seed), "given as seed.")
                seeed = hash(id(seed))
        else:
            seed = random.randint(*Constants.random_seed_range)
        self.seed = seed
        if name == "":
            name = Defaults.WorldFile.default_world_name
        # self.world_file = world_files.new_world(os.path.join(mypath, "saves"), name, gamemode, seed)
        self.world = WorldServerSide(CHUNK_SIZE_X, CHUNK_SIZE_Y, WorldGenerator(CHUNK_SIZE_X, CHUNK_SIZE_Y, seed=seed))
        self.world_generator = self.world.generator
        self.main_player = Player(self, username, hitbox=Hitbox(0,0,*Constants.Player.size))

        self.world.addChunk(0, self.world_generator.generateChunk(0))
        self.world.addPlayer(self.main_player)
        log(f"Player spawned on xy: {self.main_player.hitbox.x}, {self.main_player.hitbox.y}")
        self.world.tick()
        self.world_file = world_files.WorldFile(self.world, os.path.join(GAME_DIR, Defaults.WorldFile.default_saves_dir), name)

    def load_world(self, path, username):
        self.world = WorldServerSide(CHUNK_SIZE_X, CHUNK_SIZE_Y)
        with open(path, "r") as f:
            file_data = "".join(f.readlines())
        self.world.loadFromDict(self, world_files.WorldFile.loadFileDataIntoDict(file_data))
        try:
            self.main_player = [player for player in self.world.players if player.name == username][0]
        except Exception as e:
            log(f"Error in InternalServer.load_world(): Error loading main player: {e}.\nExpected username: {username}.\nCreating player...")
            self.world.addPlayer(Player(self, username))
        self.world_generator = self.world.generator
        self.world_file = world_files.WorldFile(self.world, os.path.join(GAME_DIR, Defaults.WorldFile.default_saves_dir), ".".join(os.path.basename(path).split(".")[:-1]), overwrite = True)
    
    def close(self):
        self.world_file.save()
    
class socketClient:
    def __init__(self, game):
        self.game = game
        self.encoding_type = "utf-8"
        self.connected = False
        self.nickname = f"Guest{random.randint(10000,99999)}"
        self.auth = str(random.randint(10000,99999))
    def flagMaker(self, *args, **kwargs):
        self.game.setFlag(*args, **kwargs)
    def receiveTCP(self, tcp:socketModules.ClientTCP, flagMaker):
        global running
        register_thread(threading.current_thread())

        while self.connected and running:
            try:
                msg, addr = tcp.client.recvfrom(1024)
                if addr != self.game.serverAddr:
                    log(f"Error: Received message from wrong address: {addr}", color="red")
                    log(f"Error: Received message from wrong address: {addr}", color="red")
                    log(f"Error: Received message from wrong address: {addr}", color="red")
                    continue
                msg = msg.decode(self.encoding_type)
                msg_type, msg = msg[0:2], msg[2:]
                if msg_type == ProtocolTCP.ToClient.connected:
                    log("Connected TCP!")
                elif msg_type == ProtocolTCP.ToClient.disconnected:
                    log("Disconnected TCP!")
                elif msg_type == ProtocolTCP.ToClient.answerChunk:
                    log("Received blockmap!")
                    self.flagMaker("blockMap", msg)
                elif msg_type == ProtocolTCP.ToClient.error:
                    log("Error:", msg)
                elif msg_type == ProtocolTCP.ToClient.playerList:
                    log("Received player list!")
                    self.flagMaker("playerList", msg)
                elif msg_type == ProtocolTCP.ToClient.playerAdded:
                    log("Received player added!")
                    self.flagMaker("playerAdded", msg)
                elif msg_type == ProtocolTCP.ToClient.playerRemoved:
                    log("Received player removed!")
                    self.flagMaker("playerRemoved", msg)
                elif msg_type == ProtocolTCP.ToClient.checkConnection:
                    log("Received check connection!")
                    self.flagMaker("sendToServer", ProtocolTCP.ToServer.answerCheckConnection)
            except Exception as e:
                log(f"Error in receiveTCP: {e}")
        unregister_thread(threading.current_thread())
    def receiveUDP(self, udp:socketModules.ClientUDP, flagMaker):
        global running
        register_thread(threading.current_thread())

        while self.connected and running:
            try:
                msg, addr = udp.recvfrom(1024)
                msg = msg.decode(self.encoding_type)
                msg_type, msg = msg[0:2], msg[2:]
                if msg_type == ProtocolUDP.ToClient.playerMoved:
                    log("Received player moved:")
                    log(msg)
                else:
                    log("Unknown UDP message:", msg_type, msg)
            except Exception as e:
                log(f"Error in receiveUDP: {e}")
        unregister_thread(threading.current_thread())
    def connect(self, ip:str, port:int):
        log("Trying to connect...")
        self.tcp:socketModules.ClientTCP = socketModules.ClientTCP(self.flagMaker, logger=log)
        self.udp:socketModules.ClientUDP = socketModules.ClientUDP(self.flagMaker, logger=log)
        try:
            for try_idx in range(5):
                try:
                    self.tcp.connect(ip, port, self.udp.port, self.nickname, self.auth)
                    msg, addr = self.tcp.client.recvfrom(1024)
                    msg = msg.decode(self.encoding_type)
                    if msg[0:2] == ProtocolTCP.ToClient.connected:
                        log("Connected TCP!")
                    else:
                        log("Error connecting TCP (server errror response):", msg[:2], msg[2:])
                        raise Exception(msg)
                    self.udp.connect(ip, port, self.nickname, auth=self.auth)
                    log("Connected UDP!")
                    self.flagMaker("connectWorld")
                    self.connected = True
                    break
                except Exception as e:
                    log(f"Try {try_idx} failed: e:{e}")
                    try:
                        self.tcp.close()
                        self.udp.close()
                    except:
                        pass
                    time.sleep(0.5)
            self.receiveThreadTCP = threading.Thread(target=self.receiveTCP, args=(self.tcp, self.flagMaker), daemon=True)
            self.receiveThreadUDP = threading.Thread(target=self.receiveUDP, args=(self.udp, self.flagMaker), daemon=True)
            self.receiveThreadTCP.start()
            self.receiveThreadUDP.start()
        except Exception as e:
            log("[Error]: Connection failed: ", e)
            global running
            running = False
        if self.connected == False:
            log("Failed to connect server")
    def checkConnection(self):
        self.tcp.send(ProtocolTCP.ToServer.checkConnection)
    def getChunkData(pos):
        pass
    def close(self):
        try:
            self.tcp.send(ProtocolTCP.ToServer.requestDisconnection)
        except Exception as e:
            log(f"Error sending disconnect message: {e}")
        self.connected = False
        try:
            self.tcp.close()
            self.udp.close()
        except Exception as e:
            log(f"Error disconnecting: {e}")
        log("Disconnected from server")
class Game:
    def __init__(self, TPS=60, FlagChecksPerSecond=20):
        self.displayManager = DisplayManager(gui.defaultGameGuiHandler(WINDOW_WIDTH, WINDOW_HEIGHT, gui_textures, self.setFlag), self)
        self.mouseInput = MouseInput()
        self.waitingForResponse = []
        self.TPS = TPS
        self.flags = []
        self.FlagChecksPerSec = FlagChecksPerSecond
        self.socketClient = None#socketClient(self)
        self.InternalServer = None
        self.server = None
        self.ingame = False
        self.clock = pygame.time.Clock()
        self.player = None
        self.world_file = None
        self.UserName = "Herobrine"
    def setFlag(self, *args, **kwargs):
        """
        Create flag for game system.
        - :args
              - If 'Flag' object is passed, it will be added to flags.
              - Elseway flag will be created using first argument as flag type.
        - :kwargs
              - If Flag was passed in args, nothing happens
              - In other case, kwargs will be added to the flag
        """
        if type(args[0]) == Flag:
            self.flags.append(args[0])
        else:
            self.flags.append(Flag(args[0], *args[1:], **kwargs))
    def startTicking(self):
        tickThread = threading.Thread(target=self.tickThreadFunc)
        tickThread.start()
        flagCheckingThread = threading.Thread(target=self.flagChecking)
        flagCheckingThread.start()
    def _move_player(self, mouse_click, events, mouse_pos):
        self.InternalServer.main_player.move(KEYS)
    def _check_block_interactions(self, cursor_world_pos, mouse_click, mouse_buttons_states):
        #TODO
        if mouse_buttons_states[0]:
            log("BLOCK BREAKING")
            try:
                self.InternalServer.world.setBlock(*cursor_world_pos, 0)
            except:
                pass
        if mouse_buttons_states[2] and self.InternalServer.world.getBlock(*cursor_world_pos) == 0:
            log("BLOCK SETTING")
            hitbox = self.InternalServer.main_player.hitbox
            if not (math.floor(hitbox.x) <= cursor_world_pos[0] <= math.ceil(hitbox.x + hitbox.width) and math.floor(hitbox.y) <= cursor_world_pos[1] <= math.ceil(hitbox.y + hitbox.height)):
                self.InternalServer.world.setBlock(*cursor_world_pos, 1)
                    
    def tickThreadFunc(self):
        global running
        register_thread(threading.current_thread())
        # target_time_per_tick = 1 / self.TPS  # Time per tick in seconds
        tick = 0
        try:
            while running:
                mouse_click, events, mouse_pos, mouse_buttons_states = self.mouseInput.read()
                self.displayManager.tick(mouse_click, events, mouse_pos)
                if self.ingame:
                    self._move_player(mouse_click, events, mouse_pos)
                    self._check_block_interactions(self.displayManager.renderer.cursor_world_pos, mouse_click, mouse_buttons_states)
                    if tick % (self.TPS * Constants.World.GenChecksPerSec) == 0:
                        self.InternalServer.world.tick()
                # log("TPS")
                self.clock.tick(self.TPS)
                tick += 1
        except pygame.error as e:
            log("Error in tickThreadFunc:", e)
            self.running = False
        unregister_thread(threading.current_thread())
    def flagChecking(self):
        global running
        register_thread(threading.current_thread())
        target_time_per_check = 1 / self.FlagChecksPerSec
        while running:
            start_time = time.time()
            response = self.checkFlags()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, target_time_per_check - elapsed_time)
            time.sleep(sleep_time)
        unregister_thread(threading.current_thread())
    def checkFlags(self):
        self.serverAddr = (LOCALHOST, DEFAULT_PORT)
        if self.flags:
            flag = self.flags[0]
            log("FLAG", flag)
            match flag.type:
                case "newWorld":
                    log("Initializing internal server...", color="blue")
                    self.InternalServer = InternalServer()
                    log("Creating new world...")
                    self.InternalServer.new_world(flag.kwargs["name"],flag.kwargs["gamemode"],self.UserName,seed=flag.kwargs["seed"])
                    log("Starting internal server...")
                    self.InternalServer.start()
                    log("Internal server started!", color="green")
                    log("Starting renderer", color="blue")
                    self.displayManager.state = "game"
                    self.displayManager.renderer = Renderer(screen, self.InternalServer.world,TrackingCamera(self.InternalServer.main_player),ConfigFiles.UI_CONFIG_FILE,self.mouseInput,self)
                    log("Renderer started!", color="green")
                    self.displayManager.guiManager.menu_collection.current_menu_idx = self.displayManager.guiManager.menu_collection.tree.find("Game")
                    self.ingame = True
                    # sys.path = os.path.dirname(SERVER_FILE_PATH)
                    # import server3 as SERVER_IMPORT
                    # sys.path = mypath
                    # self.server = SERVER_IMPORT.server #Server("", offline=True)
                    # self.serverRequestQueue = self.server.requestQueue
                    # log("Creating new world with params:", flag.args, flag.kwargs, color="green")
                    # self.setFlag(Flag("connectWorld", "offline"))
                    # log("Creating new worls with params:", flag.args, flag.kwargs)
                    # log(f"Starting server by command: {" ".join([PYTHON_BASH_COMMAND, SERVER_FILE_PATH, self.serverAddr[0], str(self.serverAddr[1])])}")
                    # self.server = subprocess.Popen(" ".join([PYTHON_BASH_COMMAND, SERVER_FILE_PATH, self.serverAddr[0], str(self.serverAddr[1]), *flag.args, *flag.kwargs]), stdout=subprocess.PIPE, shell=True)
                    # self.setFlag(Flag("connectServer", LOCALHOST, DEFAULT_PORT))
                case "loadWorld":
                    world_filename = world_files.prompt_file(Defaults.WorldFile.default_saves_dir)
                    log("World file: ", world_filename)
                    if not world_filename:
                        log("No file selected. Aborting...")
                    else:
                        log("Initializing internal server...", color="blue")
                        self.InternalServer = InternalServer()
                        log("Loading world from file...")
                        self.InternalServer.load_world(world_filename, self.UserName)
                        log("Starting internal server...")
                        self.InternalServer.start()
                        log("Internal server started!", color="green")
                        log("Starting renderer", color="blue")
                        self.displayManager.state = "game"
                        self.displayManager.renderer = Renderer(screen, self.InternalServer.world,TrackingCamera(self.InternalServer.main_player),ConfigFiles.UI_CONFIG_FILE,self.mouseInput,self)
                        log("Renderer started!", color="green")
                        self.displayManager.guiManager.menu_collection.current_menu_idx = self.displayManager.guiManager.menu_collection.tree.find("Game")
                        self.ingame = True
                    # self.server = SourceFileLoader(SERVER_FILE_PATH.split("/")[-1][:3],SERVER_FILE_PATH).load_module()
                    # self.server = self.server.Server(offline=True, world_file=flag.args[0])
                    # self.setFlag(Flag("connectWorld", "offline"))
                    # log(f"Starting server by command: {" ".join([PYTHON_BASH_COMMAND, SERVER_FILE_PATH, self.serverAddr[0], str(self.serverAddr[1])])}")
                    # log("Loading world with params:", flag.args, flag.kwargs)
                    # self.server = subprocess.Popen(" ".join([PYTHON_BASH_COMMAND, SERVER_FILE_PATH, self.serverAddr[0], str(self.serverAddr[1]), *flag.args, *flag.kwargs]), stdout=subprocess.PIPE, shell=True)
                    # self.setFlag(Flag("connectServer", LOCALHOST, DEFAULT_PORT))
                case "connectServer":
                    try:
                        log(f"Connecting server on {flag.args}")
                        self.serverAddr = (flag.args[0], int(flag.args[1]))
                        self.socketClient.connect(flag.args[0], int(flag.args[1]))
                    except Exception as e:
                        print(f"[Error]: {e}")
                case "connectServerFullIP":
                    try:
                        self.setFlag("connectServer", flag.args[0].split(":")[0], int(flag.args[0].split(":")[1]))
                        self.serverAddr = (flag.args[0].split(":")[0], int(flag.args[0].split(":")[1]))
                    except:
                        pass
                case "connectWorld":
                    log("Connecting world...", color="bold")
                    if len(flag.args) > 0 and flag.args[0] == "offline":
                        # self.server.requestQueue.add(f"{ProtocolTCP.ToServer.requestChunk}0{SPLIT_CHR}0")
                        # self.waitingForResponse.append(ProtocolTCP.ToServer.requestChunk)

                        # log("Requesting chunk 0,0", color="green")
                        pass
                    else:
                        try:
                            log("Trying to connect world")
                            self.socketClient.tcp.send(ProtocolTCP.ToServer.requestChunk, 0, 0, 0, 0)
                        except Exception as e:
                            log("Error trying to connect world:", e)
                    
                    # responseCheckThread =threading.Thread(target=self.checkResponses)
                    # responseCheckThread.start()
                case "serverMessage":
                    pass
                case "changeSettings":
                    log("changesettings")
                    for key in flag.kwargs:
                        match key:
                            case "TPS":
                                self.TPS = int(flag.kwargs[key])
                            case "FPS":
                                self.FPS = int(flag.kwargs[key])
                            case _:
                                log("Unknown setting:", "key", color="warning")
                case _:
                    log("Unknown flag type:", flag.type, color = "warning")
            self.flags.pop(0)
        return status.success
    def render(self):
        if self.ingame:
            self.displayManager.renderer.render()
        else:
            self.displayManager.render()
    def exitToMenu(self):
        try:
            if self.InternalServer:
                self.InternalServer.close()
            elif self.socketClient:
                self.socketClient.close()
        except Exception as e:
            log("Error closing socket client:", e)
        try:
            if self.server:
                self.server.close()
        except Exception as e:
            log("Error closing server:", e)


def main():
    global gui_textures, screen, running, WINDOW_WIDTH, WINDOW_HEIGHT

    clock = pygame.time.Clock()
    gui_textures = texture_loader.load_gui_textures()

    game = Game(TPS=Constants.TPS)
    running = True
    resizing = False
    resize_timer = 0
    RESIZE_DELAY = 0.5
    new_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    TEXT_RESIZING = pygame.font.Font(None, 32).render("RESIZING WINDOW...", False, (255,255,255))
    game.startTicking()
    while running or threads_running:
        screen.fill((0,0,0))
        mouse_click = False
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                log(f"Waiting for threads to finish: {threads_running}", color="blue")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_click = True
            elif event.type == pygame.KEYDOWN:
                KEYS[event.key] = True
            elif event.type == pygame.KEYUP:
                KEYS[event.key] = False
            elif event.type == pygame.VIDEORESIZE:
                new_size = (event.w, event.h)
                resizing = True
                resize_timer = RESIZE_DELAY

        if resizing:
            screen.blit(TEXT_RESIZING, (pygame.display.get_window_size()[0]//2-TEXT_RESIZING.get_width()//2,pygame.display.get_window_size()[1]//2-TEXT_RESIZING.get_height()//2))
            resize_timer -= clock.get_time() / 1000
            if resize_timer <= 0:
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
                WINDOW_WIDTH, WINDOW_HEIGHT = new_size
                game.displayManager.guiManager = gui.defaultGameGuiHandler(WINDOW_WIDTH, WINDOW_HEIGHT, gui_textures, setflag=game.setFlag, currentMenuIdx=game.displayManager.guiManager.menu_collection.current_menu_idx)
                resizing = False
        else:
            game.mouseInput.update(mouse_click, events, mouse_pos, pygame.mouse.get_pressed())
            game.render()
        pygame.display.flip()
        # log("FPS")
        clock.tick(FPS)
    # game.exitToMenu()
    close_log_files()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "-p": #PROFILER
        import cProfile
        cProfile.run("main()", sort="tottime")
    else:
        main()


    
