

# class UIConfig:
#     class Hotbar:
#         texture_path = "./assets/textures/GUI/inventory/hotbar.png"
#         def __init__(self, WINDOW_WIDTH, WINDOW_HEIGHT):
#             self.size = [0.81*WINDOW_WIDTH, 0.09*WINDOW_WIDTH]
#             self.pos = [0.10*WINDOW_WIDTH, 0.87*WINDOW_HEIGHT]

import pygame
import _config
from _config import fullPath
from item import Item
import math
import keybinds

# try:
#     log()
# except:
#     def log(*a): print(*a)

def format_number(reference_surface, n1, n2, WINDOW_WIDTH, WINDOW_HEIGHT, log):    
    # parse string to number - trying to mimic CSS foramtting
    # Example usage: format_number(screen, *self.input_size, *screen.get_size(), self.log)
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

# Btw good music: https://www.youtube.com/watch?v=JDL95sZH3aU
# Nice for programming

class GameUIElement:
    def __init__(self, data:dict, KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput):
        self.log = log
        self.game_obj = game_obj
        self.gameTextures = gameTextures
        self.Keybinds = Keybinds
        self.mouseInput = mouseInput
        try:
            texture_path, texture_pos, texture_size = data["texture_path"], data["pos"], data["size"]
        except Exception as e:
            log(f"Error loading UI element: {e}")
        self.input_size = texture_size
        self.input_pos = texture_pos

        # These three will be updated on first render ;)
        self.texture_pos = (None, None)
        self.texture_size = (None, None)
        self.screen_size = (None, None)
        # -------------------------------------------

        self.texture_path = texture_path
        self.texture = pygame.image.load(texture_path).convert_alpha()
        self.KEYDICT = KEYDICT  # Reference to a global dictionary that stores data about pressed keys (passed from main script)

    def update(self, events):
        pass

    def render(self, screen):
        if self.screen_size != screen.get_size():
            
            self.texture_size = format_number(screen, *self.input_size, *screen.get_size(), self.log)

            self.texture_pos = format_number(screen, *self.input_pos, *screen.get_size(), self.log)
            # log("GUI_ELEMENT_RENDER", self.pos, self.size)

            self.texture = pygame.transform.scale(self.texture, self.texture_size)
            
        screen.blit(self.texture, self.texture_pos)

class Hotbar(GameUIElement):
    def __init__(self, data, KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput):
        SLOT_AMOUNT = 9
        KEYBINDS = {
            keybinds.Keybinds["hotbar_1"]:0,
            keybinds.Keybinds["hotbar_2"]:1,
            keybinds.Keybinds["hotbar_3"]:2,
            keybinds.Keybinds["hotbar_4"]:3,
            keybinds.Keybinds["hotbar_5"]:4,
            keybinds.Keybinds["hotbar_6"]:5,
            keybinds.Keybinds["hotbar_7"]:6,
            keybinds.Keybinds["hotbar_8"]:7,
            keybinds.Keybinds["hotbar_9"]:8,
        }
        super().__init__(data, KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput)
        try:
            self.current_selected_slot = data["current_selected_slot"]
        except KeyError:
            self.current_selected_slot = 0
        self.selected_slot_texture = pygame.image.load(data["selected_slot_texture_path"]).convert_alpha()
        self.selected_slot_texture_size = None
        self.current_selected_slot_item = None
        self.item_offset = 0
        self.item_amount_font = pygame.font.Font(None, int(data["item_amount_font_size"]))
        self.item_amount_font.set_bold(True)

    def update(self, events):
        for key in self.KEYBINDS:
            if self.KEYDICT[key]: # is the keybind pressed?
                self.current_selected_slot = self.KEYBINDS[key]
                self.log(f"Changing selected slot to: {self.current_selected_slot}")
        self.current_selected_slot_item = self.game_obj.InternalServer.main_player.inventory.get_slot(self.current_selected_slot)
        # self.log(f"Holding item: {self.current_selected_slot_item.item_id}")

    def render(self, screen):
        if self.screen_size != screen.get_size():
            self.hotbar_texture_size = format_number(screen, *self.input_size, *screen.get_size(), self.log)
            self.hotbar_texture_pos = format_number(screen, *self.input_pos, *screen.get_size(), self.log)
            self.texture = pygame.transform.scale(self.texture, self.hotbar_texture_size)

            self.selected_slot_texture_size = (self.hotbar_texture_size[1], self.hotbar_texture_size[1])
            self.selected_slot_texture = pygame.transform.scale(self.selected_slot_texture, self.selected_slot_texture_size)
            
            self.item_size = (self.hotbar_texture_size[1] * 0.7, self.hotbar_texture_size[1] * 0.7)
            self.item_offset = (self.hotbar_texture_size[1] - self.item_size[0])//2
            
        screen.blit(self.texture, self.hotbar_texture_pos)
        selected_slot_texture_pos = (self.hotbar_texture_pos[0] + self.hotbar_texture_size[1]*self.current_selected_slot, self.hotbar_texture_pos[1])
        screen.blit(self.selected_slot_texture, selected_slot_texture_pos)
        for i in range(_config.Constants.Inventory.width):
            item = self.game_obj.InternalServer.main_player.inventory.get_slot(i)
            if not item:
                continue
            item_texture = pygame.transform.scale(self.gameTextures.block_textures[item.item_id], self.item_size)
            item_texture_pos = (self.hotbar_texture_pos[0] + self.hotbar_texture_size[1]*i + self.item_offset, self.hotbar_texture_pos[1] + self.item_offset)
            screen.blit(item_texture, item_texture_pos)
            
            if item.amount != 1:
                item_amount_surface = self.item_amount_font.render(str(item.amount), False, (0,0,0))
                item_amount_surface_size = item_amount_surface.get_size()
                screen.blit(item_amount_surface, (item_texture_pos[0]+self.hotbar_texture_size[1]-self.item_offset-item_amount_surface_size[0],
                                                item_texture_pos[1]+self.hotbar_texture_size[1]-self.item_offset-item_amount_surface_size[1]))
                    

    def get_selected_slot(self):
        return self.current_selected_slot
    
class InventoryUI(GameUIElement):
    def __init__(self, data, KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput):
        super().__init__(data, KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput)
        self.shown = False
        self.keybind_released = True
        # print(type(self.texture_size[0]), type(self.texture_size[1]))
        self.hightlighted_slot_texture = pygame.image.load(data["hightlighted_slot_texture"]).convert_alpha()
        self.item_offset = 0
        self.item_size = 0
        self.item_amount_font = pygame.font.Font(None, int(data["item_amount_font_size"])) 
        self.item_amount_font.set_bold(True)
        self.mouse_item_scale_to_normal_item = float(data["mouse_item_scale_to_normal_item"])
        self.last_targeted_slot = -1

    def update(self, events):
        if self.KEYDICT[self.Keybinds["inventory"]] and self.keybind_released:
            if self.shown:
                self.game_obj.lock_movement = False
                self.shown = False
            else:
                self.game_obj.lock_movement = True
                self.shown = True
        # print(f"{self.Keybinds["inventory"]} is {"not" if keybind_pressed else "in fact"} pressed")
        self.keybind_released = not self.KEYDICT[self.Keybinds["inventory"]]
    def getScreenPosOfSlotId(self, _id):
        x = _id % _config.Constants.Inventory.width
        y = _config.Constants.Inventory.height - 1 - (_id // _config.Constants.Inventory.width)
        return (self.texture_pos[0] + x*self.texture_size[0], 
                self.texture_pos[1] + y*self.texture_size[1])
    def getSlotIdFromScreenPos(self, x, y):
        if x < self.texture_pos[0] or x >= self.texture_pos[0] + self.texture_size[0]*_config.Constants.Inventory.width:
            return -1
        elif y < self.texture_pos[1] or y >= self.texture_pos[1] + self.texture_size[1]*_config.Constants.Inventory.height:
            return -1
        grid_x = (x - self.texture_pos[0]) // self.texture_size[0]
        grid_y = (y - self.texture_pos[1]) // self.texture_size[1]
        id_ = (_config.Constants.Inventory.height-grid_y-1)*_config.Constants.Inventory.width + grid_x
        return int(id_)
    
    def render(self, screen):
        if self.screen_size != screen.get_size():
            self.texture_size = format_number(screen, *self.input_size, *screen.get_size(), self.log)
            self.texture_pos = format_number(screen, *self.input_pos, *screen.get_size(), self.log)
            self.texture = pygame.transform.scale(self.texture, self.texture_size)
            self.hightlighted_slot_texture = pygame.transform.scale(self.hightlighted_slot_texture, (self.texture_size[0], self.texture_size[1]))
            
            self.item_size = int(self.texture_size[0] * 0.7), int(self.texture_size[1] * 0.7)
            self.item_offset = (self.texture_size[0] - self.item_size[0])//2

        if self.shown:
            slot_id = 0
            highlighted_slot = self.getSlotIdFromScreenPos(*self.mouseInput.mouse_pos)
            for x in range(_config.Constants.Inventory.width):
                for y in range(_config.Constants.Inventory.height):
                    # slot_pos = (self.texture_pos[0] + self.texture_size[0]*x, self.texture_pos[1] + self.texture_size[1]*y)
                    slot_screen_pos = self.getScreenPosOfSlotId(slot_id)
                    screen.blit(self.texture, slot_screen_pos)
                    slot_id += 1
            slot_id = 0
            for x in range(_config.Constants.Inventory.width):
                for y in range(_config.Constants.Inventory.height):
                    slot_screen_pos = self.getScreenPosOfSlotId(slot_id)
                    if highlighted_slot != -1 and highlighted_slot == slot_id:
                        screen.blit(self.hightlighted_slot_texture, slot_screen_pos)
                    item = self.game_obj.InternalServer.main_player.inventory.get_slot(slot_id)
                    if item:
                        item_texture = pygame.transform.scale(self.gameTextures.block_textures[item.item_id], (self.item_size[0], self.item_size[1]))
                        screen.blit(item_texture, (slot_screen_pos[0]+self.item_offset, slot_screen_pos[1]+self.item_offset))
                        
                        if item.amount != 1:
                            item_amount_surface = self.item_amount_font.render(str(item.amount), False, (0,0,0))
                            item_amount_surface_size = item_amount_surface.get_size()
                            screen.blit(item_amount_surface, (slot_screen_pos[0]+self.texture_size[0]-self.item_offset-item_amount_surface_size[0],
                                                            slot_screen_pos[1]+self.texture_size[1]-self.item_offset-item_amount_surface_size[1]))
                        
                    slot_id += 1

            # MOUSE HELD ITEM
            item = self.game_obj.InternalServer.main_player.inventory.mouse_slot
            if item:
                item_texture = pygame.transform.scale(self.gameTextures.block_textures[item.item_id], (self.item_size[0]*self.mouse_item_scale_to_normal_item, self.item_size[1]*self.mouse_item_scale_to_normal_item))
                item_pos = (self.mouseInput.mouse_pos[0] - item_texture.get_size()[0]/2,
                            self.mouseInput.mouse_pos[1] - item_texture.get_size()[1]/2)
                screen.blit(item_texture, item_pos)

                if item.amount != 1:
                    item_amount_surface = self.item_amount_font.render(str(item.amount), False, (0,0,0))
                    item_amount_surface_size = item_amount_surface.get_size()
                    screen.blit(item_amount_surface, (item_pos[0]+(self.texture_size[0]-self.item_offset)*self.mouse_item_scale_to_normal_item-item_amount_surface_size[0],
                                                      item_pos[1]+(self.texture_size[1]-self.item_offset)*self.mouse_item_scale_to_normal_item-item_amount_surface_size[1]))
                    



            # ---------------- ITEM ACTIONS -- START -----------------#
            current_targeted_slot = self.getSlotIdFromScreenPos(*self.mouseInput.mouse_pos)
            if current_targeted_slot != -1:
                if self.mouseInput.right_button_just_pressed:
                    held_item = self.game_obj.InternalServer.main_player.inventory.mouse_slot
                    slot_item = self.game_obj.InternalServer.main_player.inventory.get_slot(highlighted_slot)
                    if held_item is None or slot_item is None or held_item.item_id != slot_item.item_id:
                        carry = self.game_obj.InternalServer.main_player.inventory.mouse_slot
                        self.game_obj.InternalServer.main_player.inventory.mouse_slot = self.game_obj.InternalServer.main_player.inventory.get_slot(highlighted_slot)
                        self.game_obj.InternalServer.main_player.inventory.set_slot(highlighted_slot, carry)
                    else:
                        items_transfered = min(_config.Constants.Inventory.max_stack_size - slot_item.amount, held_item.amount)
                        slot_item.amount += items_transfered
                        held_item.amount -= items_transfered
                        if held_item.amount <= 0:
                            self.game_obj.InternalServer.main_player.inventory.mouse_slot = None

                if self.mouseInput.left_button_just_pressed or (current_targeted_slot != self.last_targeted_slot and self.mouseInput.button_states[2]):
                    held_item = self.game_obj.InternalServer.main_player.inventory.mouse_slot
                    slot_item = self.game_obj.InternalServer.main_player.inventory.get_slot(highlighted_slot)
                    if held_item is None:
                        if self.mouseInput.left_button_just_pressed:
                            self.game_obj.InternalServer.main_player.inventory.mouse_slot = Item(slot_item.item_id, math.ceil(slot_item.amount/2))
                            slot_item.amount = math.floor(slot_item.amount/2)
                            if slot_item.amount == 0:
                                self.game_obj.InternalServer.main_player.inventory.set_slot(highlighted_slot, None) 
                    elif slot_item is None:
                        self.game_obj.InternalServer.main_player.inventory.set_slot(highlighted_slot, Item(held_item.item_id, amount=1))
                        held_item.amount -= 1
                        if held_item.amount <= 0:
                            self.game_obj.InternalServer.main_player.inventory.mouse_slot = None
                        # self.game_obj.InternalServer.main_player.inventory.set_slot(highlighted_slot, held_item)
                        # self.game_obj.InternalServer.main_player.inventory.mouse_slot = None
                    elif held_item.item_id == slot_item.item_id:
                        items_transfered = 1#min(_config.Constants.Inventory.max_stack_size - slot_item.amount, held_item.amount)
                        slot_item.amount += items_transfered
                        held_item.amount -= items_transfered
                        if held_item.amount <= 0:
                            self.game_obj.InternalServer.main_player.inventory.mouse_slot = None
                    elif held_item.item_id != slot_item.item_id and slot_item is None:
                        carry = self.game_obj.InternalServer.main_player.inventory.mouse_slot
                        self.game_obj.InternalServer.main_player.inventory.mouse_slot = self.game_obj.InternalServer.main_player.inventory.get_slot(highlighted_slot)
                        self.game_obj.InternalServer.main_player.inventory.set_slot(highlighted_slot, carry)
            self.last_targeted_slot = self.getSlotIdFromScreenPos(*self.mouseInput.mouse_pos)
            # ---------------- ITEM ACTIONS -- END -----------------#


class GameUI:
    def __init__(self, KEYDICT:dict, log, game_obj, gameTextures, Keybinds, mouseInput):
        self.elements:list = {"hotbar":Hotbar, "inventory":InventoryUI} # Actual size of hotbar texture is 724x84
        self.elements_config:list[dict] = [{ # HOTBAR
            "texture_path":fullPath("./assets/textures/GUI/inventory/hotbar.png"),
            "size":["63vw", "7vw"],
            "pos":["25vw", "90vh"],
            "selected_slot_texture_path":fullPath("./assets/textures/GUI/inventory/selected.png"),
            "item_amount_font_size":20
        },
        { # INVENTORY
            "texture_path":fullPath("./assets/textures/GUI/inventory/slot.png"),
            "hightlighted_slot_texture":fullPath("./assets/textures/GUI/inventory/selected.png"),
            "size":["10vw", "10vw"],
            "pos":["5vw", "20vh"],
            "item_amount_font_size":20,
            "mouse_item_scale_to_normal_item":1
        }]
        self.element_to_manage_current_selected_slot = "hotbar"
        self.game_obj = game_obj
        self.gameTextures = gameTextures
        self.log = log
        self.Keybinds = Keybinds
        self.mouseInput = mouseInput

        # OK there is some terrible code down there, but it's only temporary
        # ...
        #      'Nothing is more permanent than temporary fix'
        #                                    -Some youtuber
        for i, key in enumerate(self.elements.keys()):
            self.elements[key] = self.elements[key](self.elements_config[i], KEYDICT, log, game_obj, gameTextures, Keybinds, mouseInput)
            # UI elements dont need to know screen size on init, they will update on the first render()


    def update(self, events):
        for key in self.elements:
            self.elements[key].update(events)

    def render(self, screen):
        for key in self.elements:
            self.elements[key].render(screen)

    def get_selected_slot(self):
        try:
            return self.elements[self.element_to_manage_current_selected_slot].get_selected_slot()
        except Exception as e:
            self.log(f"Error in GameUI.get_selected_slot(): {e}", color="error")
            return -1