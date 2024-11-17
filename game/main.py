from world_render import get_screen_pos, Point2d, block_size, block_in_screenX, block_in_screenY
from texture_loader import gui_folder, block_names, block_texture_files, not_full, block_texture_id, list_breaking_time, cursor_folder, texture_folder, sound_folder, music_folder, sound_list, random_sound, load_textures_and_sounds, item_size
from world import Chunk, World, chunk_size_y, chunk_size_x
# from player import defaultPlayer
from inventory import Inventory
from button import Button
from switch_button import SwitchButton
import world_files
import pygame
import sys
import keys
import math
import os
import socket
import json
import threading
import gameExceptions
from textinput import TextInput
import socket_.client as socket_client
import socket
import time
running = True
framerate = 30
multiplayer_mode = False
# Initialize Pygame
pygame.init()

# Set up the display 
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
prerender = pygame.Surface((block_size*(block_in_screenX-1), block_size*(block_in_screenY-1)))
pygame.display.set_caption("Paper minecraft - indev")
#pygame.display.set_mode((width,height),pygame.locals.RESIZABLE)

# "if true" - I know it's stupid :D, but I want to collapse it in VScode
if True:
    block_size_add = 1

    cursor, textures, block_sounds, item_textures, player_textures, gui_textures = load_textures_and_sounds(block_size, block_size_add)
    gui_textures["main_manu_background"] = pygame.transform.scale(gui_textures["main_manu_background"],(width, height))
    # Set up the square
    square_size = 200
    square_x = (width - square_size) // 2
    square_y = (height - square_size) // 2

    key_dict = keys.keydict

    mouse_affect = 0.01
    max_camera_offset = Point2d(width/2*mouse_affect, height/2*mouse_affect)
    camx = 0
    camy = 0
    camera = Point2d(camx, camy)
    camera_offset = Point2d(0, 0)


    current_world_name = None
    update_frame_once = False
    tick = 0
    movement_speed = 64/400#block_size/156#
    movement_detail = 64/4
    player_movement_leg_angle = 0

    menus = {
        "main_menu_oppened": True,
        "ingame_main_menu_oppened": False,
        "options_menu_oppened": False,
        "file_menu_oppened": False,
        "world_menu_oppened": False,
        "open_world_menu_oppened": False,
        "update_world_menu_oppened": False,
        "multiplayer_menu_oppened": False,
        "create_world_menu_oppened": False
    }
    menus["main_menu_oppened"] = True
    # ingame_main_menu_oppened = False
    # options_menu_oppened= False
    # file_menu_oppened = False
    # open_world_menu_oppened = False
    # update_world_menu_oppened = False
    # multiplayer_menu_oppened = False
    # create_world_menu_oppened = False
    # world_menu_oppened = False

    esc_delay = False
    hide_ui = False
    selected_in_hotbar = 0
    hotbar_positions = []
    for i in range(9):
        hotbar_positions.append(width/2-360+(80*i))

    quit_button =               Button(width // 2 - 200,    height - 200,  400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Quit")
    back_button =               Button(width // 2 - 200,    200,           400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Back to game")
    options_button =            Button(width // 2 - 200,    270,           190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Options")
    done_back_to_main_button =  Button(width // 2 - 200,    height - 200,  400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Done")
    file_options_button =       Button(width // 2 + 10,     270,           190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Files")
    save_world_button =         Button(width // 2 + 10,     270,           190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Save world")
    load_world_button =         Button(width // 2 - 200,    270,           190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Load world")
    select_world_button =       Button(width // 2 - 200,    height - 200,  400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Default_world_button_text")
    update_world_button =       Button(width // 2 - 200,    340,           400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Update world")
    new_world_button =          Button(width // 2 - 200,    270,           400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Crate new world")
    multiplayer_menu_button =   Button(width // 2 - 200,    50,            400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), "Multiplayer")
    server_ip_input =           TextInput(width // 2 - 200,    270,        400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), placeholder="Server ip:port", text="127.0.0.1:5555", font_size=35, maxlen = 15)
    nickname_input =            TextInput(width // 2 - 200,    340,        400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), placeholder="Nickname", font_size=35, maxlen = 15)
    world_name_input =          TextInput(width // 2 - 200,    270,        400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), placeholder="World name", font_size=35, maxlen = 15)
    game_mode_switch =          SwitchButton(width // 2 - 200, 340,        190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), ["Creative", "Survival"], return_data = [0,1])

    #--------PLAYER SETUP-----------
    gravity = 0.05
    jump_affect = 0.5
    velocityY = 0
    gravity_max = -1
    #-----------PLAYER SETUP END------------
    current_breaking_time = 0
    breaking_pozition = Point2d(0,0)
    inventory = Inventory()
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    mouse_l = False
    mouse_r = False
    mouse_r_click = False
    events = pygame.event.get()
    last_placed_tick = -1
    placement_delay = 1
    nickname = ""
    eventqueue = []
    #last_frame = pygame.Surface((width, height))
    current_frame = pygame.Surface((width, height))
    current_frame.fill("#ccd8ff")
    last_cam_position = None
    cam_moved = [0,0]
    last_position_cam = [0,0]
    screen_update = True
    angle = 0

    event_list = {"00":"10","01":"11","02":"12"}
def render_player(player, screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=False, rotate_player=False)->None:
        #print("renderding player", player.x, player.y)
        #print("type of movement angle (player:25)", type(player_movement_leg_angle))
        # import pygame
        # import math

        # # Render body
        # body_texture = pygame.transform.scale(player_textures["body"], (player.block_size*4, player.block_size*4))
        # body_rect = body_texture.get_rect(center=(player.x + player.sizex/2, player.y + player.sizey/2))
        # screen.blit(body_texture, body_rect)

        # # Get mouse position
        # mouse_x, mouse_y = pygame.mouse.get_pos()

        # # Calculate angle between player and mouse
        # mouse_offset_x = mouse_x - (player.x + player.sizex / 2)
        # dy = mouse_y - (player.y + player.sizey / 2)
        # angle = math.atan2(dy, mouse_offset_x) % (2*math.pi)

        # # Determine which direction the head should face
        # if 0 <= angle <= math.pi:
        #     head_texture = player_textures["head_r"]
        # elif math.pi < angle < 2*math.pi:
        #     head_texture = player_textures["head_l"]
        # else:
        #     print("ERROR:", angle)
        # mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate angle between player and mouse
    mouse_offset_x = mouse_x - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[0]
    mouse_offset_y = mouse_y - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[1]
    mouse_offset_y = -mouse_offset_y
    #print("rendering on ", mouse_offset_x, mouse_offset_y)
    if not (is_game_paused_) and rotate_player:
        player.angle = math.atan2(mouse_offset_y, mouse_offset_x)
    #print(math.degrees(angle))
    if -math.pi/2 < player.angle < math.pi/2:
        t = "head_r"
    else:
        t = "head_l"
    original_texture = pygame.transform.scale(player_textures[t], (block_size*0.5, block_size*0.5))
    body_texture = pygame.transform.rotate(original_texture, math.degrees(player.angle))

    if -math.pi/2 < player.angle < math.pi/2:
        offset = pygame.math.Vector2(0, -original_texture.get_height() / 2).rotate(-math.degrees(player.angle))
    else:
        offset = pygame.math.Vector2(0, original_texture.get_height() / 2).rotate(-math.degrees(player.angle))
    #print(angle)
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.16, player.y))[0] + offset.x, get_screen_pos(camera, Point2d(player.x, player.y + 0.6))[1] + offset.y))
    screen.blit(body_texture, body_rect)
    if -math.pi/2 < player.angle < math.pi/2:
        leg_texture = player_textures["leg_l"]
    else:
        leg_texture = player_textures["leg_r"]
    body_texture = pygame.transform.scale(player_textures["body"], (block_size*0.3, block_size))
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.3/2, player.y))[0], get_screen_pos(camera, Point2d(player.x, player.y + 0.1))[1]))
    screen.blit(body_texture, body_rect)
    body_texture = pygame.transform.scale(leg_texture, (block_size * 0.29, block_size * 0.8))
    rotated_texture = pygame.transform.rotate(body_texture, player_movement_leg_angle)
    rotation_point = get_screen_pos(camera, Point2d(player.x - 0.3 / 2, player.y - 0.7))
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(player_movement_leg_angle/2))*block_size*0.29) + player.isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
    body_texture = pygame.transform.scale(leg_texture, (block_size * 0.29, block_size * 0.8))
    rotated_texture = pygame.transform.rotate(body_texture, -player_movement_leg_angle)
    rotation_point = get_screen_pos(camera, Point2d(player.x - 0.3 / 2, player.y - 0.7))
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(-player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(-player_movement_leg_angle/2))*block_size*0.29) + player.isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
def save_world(filename=None, overwrite = False):
    if current_world_name:
        world_files.save_data({"version":-1,"gamemode":str(overworld.gamemode),"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite,filename = current_world_name)
        return
    if filename:
        world_files.save_data({"version":-1,"gamemode":str(overworld.gamemode),"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite, filename = filename)
        return
    world_files.save_data({"version":-1,"gamemode":str(overworld.gamemode),"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite)
def getcode(event):
    print("Event code:", event_list[event])
    return event_list[event]
def send_to_server(event, *message):
    #00 - moved
    #01 - changed block
    sock_stream_types = ["01","02",]
    dgram_types =["00",]
    if not event in dgram_types:
        message = list(map(str, message))
        #print("Sending", getcode(event), *message)
        client_sock_stream.send(getcode(event), *message)
    # else:
    #     client_dgram.send(event, message)
def message_process(message):
    global other_players_nicknames
    data_type = message[:2]
    message = message[2:].split("\x01")
    print(data_type, message)
    match data_type:
        case "00":
            print("Connected")
            other_player_nicknames = message
        case "01":
            print("Disconnected")
            client_sock_stream.close()
            open_menu("multiplayer_menu_oppened")
        case "07":
            overworld.set_block(int(message[0]), int(message[1]), int(message[2]))
        case "11":
            try:
                overworld.set_block(int(message[0]), int(message[1]), int(message[2]))
            except Exception as e:
                print("Error placing block:", e)
                eventqueue.append(["11", *message])
        case "12":
            print("braking block")
            try:
                overworld.set_block(int(message[0]), int(message[1]), 0)
            except Exception as e:
                print("Error breaking block:", e)
                eventqueue.append(["12", *message])
        case _:
            if data_type != "06":
                print("Unknown message type:", data_type, message)
def message_process_dgram(message):
    data_type = message[:2]
    message = message[2:].split("\x01")
    match data_type:
        case "10":
            target_player = message[0]
            if not target_player in other_players_nicknames:
                other_players_nicknames.append(message[0])
                overworld.addplayer(message[0], message[1], message[2], message[3])
            index = overworld.findplayer(message[0])
            overworld.players[index].x = float(message[1])
            overworld.players[index].y = float(message[2])
            overworld.players[index].angle = float(message[3])
def connect_to_server_setup(ip, port, nick):
    global overworld, client_sock_stream, nickname, multiplayer_mode, client_dgram
    overworld = World()
    client_sock_stream = socket_client.SockStreamClient(process_function=message_process)
    client_sock_stream.connect(ip, port, nick)
    client_dgram = socket_client.SockStreamClient(process_function=message_process_dgram)
    client_dgram.connect(ip, port, nick)
    client_thread_sock_stream = threading.Thread(target=client_sock_stream.receive)
    client_thread_sock_stream.start()
    client_thread_dgram = threading.Thread(target=client_dgram.receive)
    client_thread_dgram.start()
    nickname = nick
    multiplayer_mode = True
# def open_menu(menu:str, all_other_false = True, disable_mouse_click = True, notraise=False):
#     global world_menu_oppened, menus["create_world_menu_oppened"], menus["create_world_menu_oppened"], menus["multiplayer_menu_oppened"],menus["main_menu_oppened"], menus["file_menu_oppened"], menus["ingame_main_menu_oppened"], menus["options_menu_oppened"], menus["open_world_menu_oppened"], menus["update_world_menu_oppened"]
#     #print(menu, "is true")
#     match menu:
#         case "main_menu_oppened":
#            menus["main_menu_oppened"] = True
#         case "menus["file_menu_oppened"]":
#             menus["file_menu_oppened"] = True
#         case "menus["ingame_main_menu_oppened"]":
#             menus["ingame_main_menu_oppened"] = True
#         case "menus["options_menu_oppened"]":
#             menus["options_menu_oppened"] = True
#         case "menus["open_world_menu_oppened"]":
#             menus["open_world_menu_oppened"] = True
#         case "menus["update_world_menu_oppened"]":
#             menus["update_world_menu_oppened"] = True
#         case "menus["multiplayer_menu_oppened"]":
#             menus["multiplayer_menu_oppened"] = True   
#         case "menus["create_world_menu_oppened"]":
#             menus["create_world_menu_oppened"] = True    
#         # case "menus["create_world_menu_oppened"]":
#         #     menus["create_world_menu_oppened"] = True
#         case "world_menu_oppened":
#             world_menu_oppened = True
#     if all_other_false:
#         for menu_name in ["world_menu_oppened", "menus["create_world_menu_oppened"]", "menus["multiplayer_menu_oppened"]", "main_menu_oppened", "menus["file_menu_oppened"]", "menus["ingame_main_menu_oppened"]", "menus["options_menu_oppened"]", "menus["open_world_menu_oppened"]", "menus["update_world_menu_oppened"]", "menus["create_world_menu_oppened"]"]:
#             if menu_name != menu:
#                 #print(menu_name, "is false")
#                 globals()[menu_name] = False 
#     if disable_mouse_click:
#         global mouse_r_click
#         mouse_r_click = False
#         #print("mouse_r_click is false")
#     if not notraise:
#         raise gameExceptions.MenuClosed
def open_menu(menu:str, all_other_false = True, disable_mouse_click = True, notraise=False):
    global menus
    if menu in menus.keys():
        menus[menu] = True

    if all_other_false:
        for i, _ in menus.items():
            if i != menu:
                menus[i] = False
    if disable_mouse_click:
        global mouse_r_click
        mouse_r_click = False
        #print("mouse_r_click is false")
    # if not notraise:
    #     raise gameExceptions.MenuClosed
def parse_chunks(x):
    output = []
    for i in x:
        output.append(i.blocks)
    return output
def parse_world(world):
    output = [[],[]]
    output[0] = parse_chunks(world.chunkpoz)
    output[1] = parse_chunks(world.chunkneg)
    return output
def load_chunk(x):
    output = []
    for i in x:
        c = Chunk()
        c.blocks = i
        output.append(c)
    return output
def load_world(data):
    global overworld, player, selected_in_hotbar
    overworld = World(not_pregen=True)
    overworld.chunkpoz = load_chunk(data["world"][0])
    overworld.chunkneg = load_chunk(data["world"][1])
    overworld.main_player.x = data["playerx"]
    overworld.main_player.y = data["playery"]
    selected_in_hotbar = data["select_in_hotbar"]
    overworld.gamemode = data["gamemode"]
def list_world_files():
    return os.listdir("saves")
def is_game_paused() -> bool:
    #print(menus["multiplayer_menu_oppened"] ormenus["main_menu_oppened"] or menus["file_menu_oppened"] or menus["ingame_main_menu_oppened"] or menus["options_menu_oppened"] or menus["open_world_menu_oppened"] or menus["update_world_menu_oppened"])
    
    return True in [i for _,i in menus.items()] #(menus["create_world_menu_oppened"] or menus["multiplayer_menu_oppened"] ormenus["main_menu_oppened"] or menus["file_menu_oppened"] or menus["ingame_main_menu_oppened"] or menus["options_menu_oppened"] or menus["open_world_menu_oppened"] or menus["update_world_menu_oppened"] or menus["create_world_menu_oppened"])
def get_sound(block_name):
    return random_sound(block_name, block_sounds)
    try:
        return block_sound[block_texture_id[block_name]]
    except:
        print("Error finding sound")
        return block_sound[0]#error_sound
#--------UTILITY FUNCTIONS-----------
def get_cursor_state_and_handle_block_breaking(block_id, breaking_time):
    if overworld.gamemode == 0 and breaking_time >= 1:
        return 100
    try:
        max_time = list_breaking_time[block_id]
    except:
        max_time = 2
    if max_time <= 0:
        if max_time == -2:
            return -1
        return 0
    if breaking_time == max_time:
        return -1
    state = math.ceil(breaking_time/max_time)
    if state > 10:
        return 100
    return state
def get_block(x, y):
    try:
        m = overworld.get_block(math.floor(x),math.floor(y))
        if type(m)==Exception:
            return 0
        return m
    except Exception as e:
        return -1
def movable(block):
    try:
        return not_full[block] 
    except:
        return False
def entity_here(x, y):
    x, y = math.floor(x), math.floor(y)
    corners = overworld.main_player.corners()
    return True in [((math.floor(corners[i][0])==x)and(math.floor(corners[i][1])==y)) for i in range(4)]
def isfree(x, y, entitywidth, entityheight):
    #    return(not (False in [movable(get_block(x, y)), movable(get_block(x + entitywidth, y)), movable(get_block(x, y + entityheight)), movable(get_block(x + entitywidth, y + entityheight))]))        

    for check_x in range(math.floor(x), math.ceil(x + entitywidth)):
        for check_y in range(math.floor(y), math.ceil(y + entityheight)):
            if not movable(get_block(check_x, check_y)):
                return False
    return True
def on_ground(playerx, playery):
    return not isfree(playerx, playery - 0.1, overworld.main_player.sizex, overworld.main_player.sizey)
def Yislegal(y):
    return 0 < y < chunk_size_y
#-----------UTILITY FUNCTIONS END------------
#--------BLOCK PLACEMENT-----------
def try_place_block(world, x, y, id):
    if Yislegal(y) and world.get_block(x, y) == 0 and (world.get_block(x, y) in not_full and not entity_here(x, y)):
        
        world.set_block(x, y, id)
        # if world.current_delay == 0:
        #     world.current_delay = world.block_sound_delay
        global screen_update
        screen_update = True
        get_sound(block_names[id]).play()
        if multiplayer_mode:
            send_to_server("01", x, y, id)
#-----------BLOCK PLACEMENT END------------
def handle_events():
    global events, running, mouse_l, mouse_r_click, mouse_r, selected_in_hotbar, ain_menu_oppened, esc_delay, menus
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key_dict[event.key] = True
        elif event.type == pygame.KEYUP:
            key_dict[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_r_click = not mouse_l
                mouse_l = True
                # if menus["ingame_main_menu_oppened"]:
                #     mouse_x, mouse_y = pygame.mouse.get_pos()
                #     button_rect = pygame.Rect(width // 2 - 100, height // 2 - 25, 200, 50)
                #     if button_rect.collidepoint(mouse_x, mouse_y):
                #         running = False
            elif event.button == 3:
                mouse_r = True
            elif event.button == 4 and not(is_game_paused()):  # Scroll up
                selected_in_hotbar = (selected_in_hotbar - 1) % 9
            elif event.button == 5 and not(is_game_paused()):  # Scroll down
                selected_in_hotbar = (selected_in_hotbar + 1) % 9
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_r_click = False
                mouse_l = False
            elif event.button == 3:
                mouse_r = False
        if key_dict[pygame.K_ESCAPE]:
            if not esc_delay:
                if menus["ingame_main_menu_oppened"]:
                    menus["ingame_main_menu_oppened"] = False
                elif menus["options_menu_oppened"]:
                    menus["options_menu_oppened"] = False
                    menus["ingame_main_menu_oppened"] = True
                else:
                    menus["ingame_main_menu_oppened"] = True
                esc_delay = True
        else:
            esc_delay = False
    if key_dict[pygame.K_F1]:
        global hide_ui
        hide_ui = not hide_ui
        key_dict[pygame.K_F1] = False 
    if key_dict[pygame.K_SEMICOLON]:
        running = False
def handle_player_movement():
    global velocityY, player_movement_leg_angle
    last_player_x = overworld.main_player.x
    if key_dict[pygame.K_a]:
        if isfree(overworld.main_player.x - movement_speed, overworld.main_player.y, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.x -= movement_speed
        elif isfree(overworld.main_player.x - movement_speed/movement_detail, overworld.main_player.y, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.x -= movement_speed/movement_detail
    if key_dict[pygame.K_d]:
        if isfree(overworld.main_player.x + movement_speed, overworld.main_player.y, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.x += movement_speed
        elif isfree(overworld.main_player.x + movement_speed/movement_detail, overworld.main_player.y, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.x += movement_speed/movement_detail
    if key_dict[pygame.K_s]:
        if isfree(overworld.main_player.x, overworld.main_player.y - movement_speed, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.y -= movement_speed
        elif isfree(overworld.main_player.x, overworld.main_player.y - movement_speed/movement_detail, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.y -= movement_speed/movement_detail
    if overworld.main_player.x - last_player_x == 0:
        player_movement_leg_angle = round((player_movement_leg_angle)/2)
    else:
        player_movement_leg_angle = (((last_player_x - overworld.main_player.x)*80 + 45) + player_movement_leg_angle) % 90 - 45
        if player_movement_leg_angle < 90:
            player_movement_leg_angle = player_movement_leg_angle
    if not isfree(overworld.main_player.x, overworld.main_player.y, overworld.main_player.sizex, overworld.main_player.sizey):
        overworld.main_player.damage(0)
        overworld.main_player.y += 0


    if True:
        if on_ground(overworld.main_player.x, overworld.main_player.y):
            if key_dict[pygame.K_w]:
                velocityY = jump_affect
            else:
                velocityY = 0
        else:
            velocityY += (gravity_max-velocityY)*gravity
        if not isfree(overworld.main_player.x, overworld.main_player.y+velocityY, overworld.main_player.sizex, overworld.main_player.sizey):
            velocityY = velocityY/2
        velocityY = round(velocityY, 2)
        if isfree(overworld.main_player.x, overworld.main_player.y + velocityY, overworld.main_player.sizex, overworld.main_player.sizey):
            overworld.main_player.y += velocityY
    if overworld.main_player.y < -10:
        overworld.main_player.damage(1)
    if multiplayer_mode:
        send_to_server("00", player.x, player.y, player.angle)
def update_camera():
    global camx, camy, camera
    camx = overworld.main_player.x
    camy = overworld.main_player.y
    camera.x = camx
    camera.y = camy
    camera.x = camx-(width/(block_size*2)) + ((mouse_x - (width/2))*(mouse_affect))
    camera.y = camy - ((mouse_y - (height/2))*(mouse_affect))
static_screen_size_x = math.ceil(block_in_screenX * 1.2)
static_screen_size_y =  math.ceil(block_in_screenY * 1.2)
def render_world():
    global last_frame, screen_update, current_frame, last_position_cam, cam_moved
    base = Point2d(int(camera.x) - 1, int(camera.y - block_in_screenY/2))
    staticx, staticy = get_screen_pos(camera, Point2d(base.x, base.y))[:2]
    cam_moved = [round(camera.x - last_position_cam[0], 3), round(camera.y - last_position_cam[1], 3)]
    if screen_update or cam_moved[0] > block_size or cam_moved[1] > block_size:
        current_frame = pygame.Surface((width, height))
        current_frame.fill(overworld.background)
        for world_x in range(static_screen_size_x):
            for world_y in range(static_screen_size_y):
                try:
                    blockx, blocky, size = staticx + (world_x*block_size), staticy - (world_y*block_size), block_size*1.2
                    current_frame.blit(textures[overworld.get_block(base.x+world_x,base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                
                except ValueError:
                    pass
        #screen.blit(current_frame, (0, 0))
        last_frame = current_frame.copy()
        screen.blit(last_frame, (0, 0))
        screen_update = True
    else:
        last_frame = current_frame.copy()
        #print("Screen update 2", cam_moved)
        # screen.fill(overworld.background)
        # screen.blit(last_frame, (0, 0))
        # return
        if cam_moved == [0,0]:
            screen.blit(last_frame, (0, 0))
            return
        base = Point2d(math.floor(camera.x) - 1, math.floor(camera.y - block_in_screenY/2))
        staticx, staticy = get_screen_pos(camera, Point2d(base.x, base.y))[:2]
        current_frame.fill((0,0,0))
        print(-cam_moved[0]*block_size, cam_moved[1]*block_size)
        current_frame.blit(last_frame, (-cam_moved[0]*block_size, cam_moved[1]*block_size))
        for world_x in range(static_screen_size_x):
            if cam_moved[1] < 0:
                try:
                    blockx, blocky, size = staticx + (world_x*block_size), staticy + (block_size), block_size*1.2
                    print(blockx, blocky, overworld.get_block(base.x + world_x,base.y))
                    current_frame.blit(textures[overworld.get_block(base.x+world_x,base.y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                
                    # blockx, blocky, size = staticx + (world_x*block_size), staticy, block_size*1.2
                    # current_frame.blit(textures[overworld.get_block(base.x + world_x,base.y)], (blockx-50, blocky-50), (0, 0, size+block_size_add, size+block_size_add))
                except ValueError:
                    raise Exception
            else:
                try:
                    blockx, blocky, size = staticx + (world_x*block_size), staticy + ((static_screen_size_y-1)*block_size), block_size*1.2
                    current_frame.blit(textures[overworld.get_block(base.x+world_x,base.y+static_screen_size_y-1)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                
                    # blockx, blocky, size = staticx + (world_x*block_size), staticy + ((static_screen_size_y-block_size)), block_size*1.2
                    # current_frame.blit(textures[overworld.get_block(base.x + world_x,base.y + ((static_screen_size_y-1)))], (blockx, blocky-600), (0, 0, size+block_size_add, size+block_size_add))
                except ValueError:
                    raise Exception
                

        for world_y in range(static_screen_size_y):
            if cam_moved[0] > 0:
                try:
                    blockx, blocky, size = staticx + block_size, staticy + (world_y*block_size), block_size*1.2
                    current_frame.blit(textures[overworld.get_block(base.x,base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                except ValueError:
                    pass
            else:
                try:
                    blockx, blocky, size = staticx + ((static_screen_size_x-1)*block_size), staticy + world_y*block_size, block_size*1.2
                    current_frame.blit(textures[overworld.get_block(base.x + ((static_screen_size_x-1)),base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                except ValueError:
                    pass
        screen.blit(current_frame, (0, 0))
    last_position_cam = [camera.x, camera.y]
def render_players():
    global mouse_x, mouse_y
    mouse_x, mouse_y = pygame.mouse.get_pos()
    #overworld.test_player.render(screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=is_game_paused())
    #overworld.main_player.render(screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=is_game_paused())
    if multiplayer_mode:
        for i in overworld.players:
            render_player(i, screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=is_game_paused())
    render_player(overworld.main_player, screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=is_game_paused(), rotate_player=True)

        #i.render(screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=is_game_paused())
    #print("rendered :D")
    # overworld.main_player.render(screen, get_screen_pos(camera, Point2d(camx, camy))[0], get_screen_pos(camera, Point2d(camx, camy))[1])
    # player_screen_pos = get_screen_pos(camera, Point2d(camx, camy))
    # pygame.draw.rect(screen, overworld.main_player.colour, (player_screen_pos[0], player_screen_pos[1]-block_size, (overworld.main_player.sizex + 0.1)*block_size, (overworld.main_player.sizey + 0.1)* block_size))
    # screen.blit(textures[5], (player_screen_pos[0], player_screen_pos[1]+overworld.main_player.sizey), (0, 0, block_size/2,block_size/2))
def break_block(x, y):
    if overworld.get_block(cursor_block_x, cursor_block_y) != block_texture_id["air"]:
        get_sound(block_names[overworld.getblock(x,y)]).play()
        if multiplayer_mode:
            send_to_server("02", x, y)
        overworld.set_block(cursor_block_x, cursor_block_y, block_texture_id["air"])
def handle_cursor_and_block_breaking(render_sqare):
    global current_breaking_time, breaking_pozition
    #print(menus["ingame_main_menu_oppened"])
    # print("Hi thre, im handling cursor O/")
    if is_game_paused():
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    if not render_sqare:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor_block_x = math.floor(camera.x + (mouse_x) / block_size)
        cursor_block_y = math.floor(camera.y - (mouse_y - height/2) / block_size) + 1
        cursor_texture_id = get_cursor_state_and_handle_block_breaking(get_block(cursor_block_x, cursor_block_y), current_breaking_time)
        if cursor_texture_id >= 0:
            if cursor_texture_id == 100:
                break_block(cursor_block_x, cursor_block_y)
                current_breaking_time = 0
                cursor_texture_id = 0
                #pygame.mixer.Sound("soung.mp3").play()
            cursor_screen_pos = get_screen_pos(camera, Point2d(cursor_block_x, cursor_block_y))
            screen.blit(cursor[cursor_texture_id], (cursor_screen_pos[0], cursor_screen_pos[1]), (0, 0, block_size+1, block_size+1))
        
        if mouse_r:
            try:
                try_place_block(overworld, cursor_block_x, cursor_block_y, block_texture_id[inventory.get_slot(selected_in_hotbar, 0)])
            except:
                pass
        if mouse_l and (breaking_pozition.x == cursor_block_x and breaking_pozition.y == cursor_block_y):
            current_breaking_time += 1
            pointing_at_block = overworld.getblock(cursor_block_x, cursor_block_y)
            if (overworld.current_delay == 0 and pointing_at_block != 0):
                overworld.current_delay = overworld.block_sound_delay 
                get_sound(block_names[pointing_at_block]).play()
        else:
            current_breaking_time = 0
            breaking_pozition.x = cursor_block_x
            breaking_pozition.y = cursor_block_y
        #print("I handled cursor propertly")
        return cursor_block_x, cursor_block_y
    else:
        return 0, 0

def render_ui(cursor_block_x:int, cursor_block_y:int):
    coordinates_text = f"X: {overworld.main_player.x:.2f}, Y: {overworld.main_player.y:.2f}"
    text_surface = font.render(coordinates_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    fps = clock.get_fps()
    fps_text = f"FPS: {fps:.2f}"
    fps_surface = font.render(fps_text, True, (255, 255, 255))
    screen.blit(fps_surface, (10, 50))
    screen.blit(gui_textures["hotbar"], [hotbar_positions[0], height - 90])
    for i in range(9):
        item = inventory.get_slot(i, 0)
        if item != None:
            try:
                screen.blit(item_textures[block_texture_id[item]], [hotbar_positions[i] + 8 - (item_size/2*0) + ((block_size - item_size)/8), height - 90 + 6 + (item_size/2*0) + ((block_size - item_size)/8)])
            except Exception as e:
                print("Error: (probably item is not loaded :D) |", e)
                print("Quitting!")
                global running
                running = False
    screen.blit(gui_textures["selected"], [hotbar_positions[selected_in_hotbar] - 4, height - 90 - 4])
    
    
def set_world(world):
    global overworld
    overworld = world

def render_gui():
    global overworld, multiplayer_mode, player, mouse_x, mouse_y, running, menus, mouse_r_click, update_frame_once, current_world_name
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if menus["ingame_main_menu_oppened"]:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))  # Add a semi-transparent black overlay
        # if multiplayer_menu_button.render(screen, mouse_r_click):
            # open_menu("menus["multiplayer_menu_oppened"]")
        if back_button.render(screen, mouse_r_click):
            open_menu(None)
        if quit_button.render(screen, mouse_r_click):
            if multiplayer_mode:
                multiplayer_mode = False
                client_sock_stream.close()
                client_dgram.close()
            else:
                save_world(overwrite=True)
            open_menu("main_menu_oppened")
        if save_world_button.render(screen, mouse_r_click, text="Save") and not multiplayer_mode:
            #open_menu("menus["create_world_menu_oppened"]")
            save_world(filename=current_world_name,overwrite=True)
            #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)})
        if options_button.render(screen, mouse_r_click):
            open_menu("options_menu_oppened")
        # if file_options_button.render(screen, mouse_r_click):
        #     open_menu("menus["file_menu_oppened"]")
    if menus["main_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        # if multiplayer_menu_button.render(screen, mouse_r_click):
        #     open_menu("menus["multiplayer_menu_oppened"]") #TODO - work in progress :D
        if quit_button.render(screen, mouse_r_click):
            #print("sry, im exiting")
            running = False
        if new_world_button.render(screen, mouse_r_click):
            open_menu("create_world_menu_oppened", notraise=True)
        if load_world_button.render(screen, mouse_r_click, y=340, width=400):
            open_menu("open_world_menu_oppened")
            #menus["main_menu_oppened"] = True
        #test_switch.render(screen, mouse_r_click)
    if menus["options_menu_oppened"]:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))  # Add a semi-transparent black overlay
        if done_back_to_main_button.render(screen, mouse_r_click):
            open_menu("ingame_main_menu_oppened")
    if menus["create_world_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        name = world_name_input.render(screen, events, [mouse_x, mouse_y, mouse_r_click], return_text=True)
        game_mode_switch.render(screen, mouse_r_click)
        if done_back_to_main_button.render(screen, mouse_r_click, x=width // 2 + 10, width=190):
            if name != "":
                world_name_input.placeholder = "World name"
                world_name_input.text = ""
                global overworld
                overworld = World()
                overworld.gamemode = game_mode_switch.getstate()
                save_world(filename=name)
                #world_files.save_data({"version":-1,"gamemode":str(overworld.gamemode),"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=name)
                open_menu(None)
                raise gameExceptions.MenuClosed()
            else:
                world_name_input.placeholder = "Please enter"
        if back_button.render(screen, mouse_r_click, x=width // 2 - 200, width=190, y=height - 200, text="Back"):
            world_name_input.placeholder = "World name"
            world_name_input.text = ""
            open_menu("main_menu_oppened")
    if menus["file_menu_oppened"]:
        if save_world_button.render(screen, mouse_r_click):
            if current_world_name == None:
                save_world()
                #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)})
            else:
                save_world(filename=current_world_name, overwrite=True)
                #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=current_world_name, filetype="", overwrite=True)
            #print("World saved")
        elif load_world_button.render(screen, mouse_r_click):
            open_menu("open_world_menu_oppened")
        elif False and update_world_button.render(screen, mouse_r_click):
            open_menu("update_world_menu_oppened")
            #load_world(world_files.load_data("new_world_button.json"))
        elif done_back_to_main_button.render(screen, mouse_r_click):
            open_menu("ingame_main_menu_oppened")
    if menus["multiplayer_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        #collision_address_button = get_collision(mouse_x, mouse_y, mouse_r_click, [server_ip_input.x, server_ip_input.y, server_ip_input.width, server_ip_input.height])
        server_address = server_ip_input.render(screen, events, return_text=True, collision = [mouse_x, mouse_y, mouse_r_click])
        nickname = nickname_input.render(screen, events, return_text=True, collision = [mouse_x, mouse_y, mouse_r_click])
        if done_back_to_main_button.render(screen, mouse_r_click, width=190, x=400):
            global server_ip
            print("Server IP:", server_ip_input.text)
            server_ip = server_address
            try:
                global client
                try:
                    client = connect_to_server_setup(*server_ip.split(":"), nickname)
                except:
                    raise gameExceptions.FailedConnectingServer
                open_menu(None)
                print("Connected to server")
            except gameExceptions.FailedConnectingServer:
                pass
            #print("Back to main menu")
        if back_button.render(screen, mouse_r_click, text="Cancel", width=190, x=200, y=height - 200):
            open_menu("main_menu_oppened")
    if menus["open_world_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        if done_back_to_main_button.render(screen,mouse_r_click):
            open_menu("main_menu_oppened")
        world_files_list = list_world_files()
        for i in range(len(world_files_list)):
            try:
                if world_files_list[i][-5:] != ".json":
                    continue
            except:
                continue
            if i > 4:
                if load_world_button.render(screen, mouse_r_click, x=width // 2 + 10, y = (i-5)*70 + 50, text = world_files_list[i]):
                    print("Loading world: ", world_files_list[i])
                    load_world(world_files.load_data(world_files_list[i]))
                    current_world_name = world_files_list[i]
                    menus["main_menu_oppened"] = False
                    menus["open_world_menu_oppened"] = False
                    if not menus["main_menu_oppened"]:
                        update_frame_once = True
            else:
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 50, text = world_files_list[i]):
                    print("Loading world: ", world_files_list[i])
                    load_world(world_files.load_data(world_files_list[i]))
                    current_world_name = world_files_list[i]
                    menus["main_menu_oppened"] = False
                    menus["open_world_menu_oppened"] = False
                    if not menus["main_menu_oppened"]:
                        update_frame_once = True
    if menus["update_world_menu_oppened"]:
        raise gameExceptions.MenuNotExist
        if done_back_to_main_button.render(screen,mouse_r_click):
            menus["update_world_menu_oppened"] = False
            menus["file_menu_oppened"] = True
        world_files_list = list_world_files()#current_world_name
        if not current_breaking_time:
            if load_world_button.render(screen, mouse_r_click, y = 50, text = f"Current: {current_world_name}"[:21]+".."):
                save_world(filename=current_world_name, overwrite=True)
                #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=current_world_name, overwrite=True)

            for i in range(len(world_files_list)):
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 120, text = world_files_list[i]):
                    save_world(world_files_list[i], overwrite=True)
                    #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=world_files_list[i], overwrite=True)
        else:            
            for i in range(len(world_files_list)):
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 50, text = world_files_list[i]):
                    save_world(world_files_list[i], overwrite=True)
                    #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=world_files_list[i], overwrite=True)
  




"""--------------------------- MAIN GAME LOOP ----------------------------------------------------------------"""
while running:
    handle_events()
    if not (menus["create_world_menu_oppened"] or menus["open_world_menu_oppened"] or menus["update_world_menu_oppened"] or menus["main_menu_oppened"] or menus["multiplayer_menu_oppened"]):
        if update_frame_once or not (is_game_paused()):
            handle_player_movement()
            update_camera()

            overworld.current_delay = max(0, overworld.current_delay-1)
            update_frame_once = False
        render_world()
        render_players()
        cursor_block_x, cursor_block_y = handle_cursor_and_block_breaking(is_game_paused())
        if not hide_ui:
            render_ui(cursor_block_x, cursor_block_y)
    if is_game_paused():
        try:
            render_gui() 
        except gameExceptions.MenuClosed:
            pass

    pygame.display.flip()

    tick = pygame.time.get_ticks()%30
    clock.tick(framerate)
    mouse_r_click = False

if multiplayer_mode:
    client_sock_stream.close()
    client_dgram.close()
pygame.quit()
sys.exit()