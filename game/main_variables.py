from world_render import Point2d, block_size, block_in_screenX, block_in_screenY
from texture_loader import load_textures_and_sounds, item_size
# from player import defaultPlayer
from inventory import Inventory
from button import Button
from switch_button import SwitchButton
import pygame
import keys
import time
from textinput import TextInput, margin
import socket_.client as socket_client

running = True
defaultFramerate = 30
tickRate = 30
framerate = defaultFramerate
multiplayer_mode = False
debug_mode:bool = False
# Initialize Pygame
pygame.init()

# Set up the display 
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
prerender = pygame.Surface((block_size*(block_in_screenX-1), block_size*(block_in_screenY-1)))
pygame.display.set_caption("Minecraft 2D")


# "if true" - I know it's stupid :D, but I want to collapse it in VScode
if True: #DEFINITION OF VARIABLES
    block_size_add = 1

    #section:graphic
    cursor, textures, block_sounds, item_textures, player_textures, gui_textures, health_bar_textures = load_textures_and_sounds(block_size, block_size_add)
    gui_textures["main_manu_background"] = pygame.transform.scale(gui_textures["main_manu_background"],(width, height))
    # Set up the square
    square_size = 200
    square_x = (width - square_size) // 2
    square_y = (height - square_size) // 2

    #section:keys
    key_dict = keys.keydict

    #section:camera
    mouse_affect = 0.01
    max_camera_offset = Point2d(width/2*mouse_affect, height/2*mouse_affect)
    camx = 0
    camy = 0
    camera = Point2d(camx, camy)
    camera_offset = Point2d(0, 0)
    update_frame_once = False

    #section:world
    overworld = None
    tick = 0
    current_world_name = None

    #section:player_movement
    movement_speed = 64/400#block_size/156#
    movement_detail = 64/4
    player_movement_leg_angle = 0

    #section:menus
    menus = {
        "main_menu_oppened": True,
        "ingame_main_menu_oppened": False,
        "options_menu_oppened": False,
        "file_menu_oppened": False,
        "world_menu_oppened": False,
        "open_world_menu_oppened": False,
        "update_world_menu_oppened": False,
        "multiplayer_menu_oppened": False,
        "create_world_menu_oppened": False,
        "chat_input_oppened": False,
        "inventory_oppened": False
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
    t_key_delay = False
    hide_ui = False
    #section:hotbar
    selected_in_hotbar = 0
    hotbar_height = height - 90 + 6 + (item_size/2*0) + ((block_size - item_size)/8)
    hotbar_positions = []
    for i in range(9):
        hotbar_positions.append(width/2-360+(80*i))

    #section:tick
    BREAK_BLOCK = False

    #section:gui
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
    chat_input =                TextInput(10,   hotbar_height,        400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), placeholder="", font_size=35, maxlen = 15)
    game_mode_switch =          SwitchButton(width // 2 - 200, 340,        190, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), ["Creative", "Survival"], return_data = [0,1])
    debug_mode_switch =         SwitchButton(width // 2 - 200, 340,        400, 50, pygame.transform.scale(gui_textures["button"], (200, 50)), ["Debug mode off", "Debug mode on"], return_data = [True,False], current_state=0 if debug_mode else 1)

    #section:ui
    ui_colour = (0,0,0)#(255, 255, 255)

    #section:player
    gravity = 0.05
    jump_affect = 0.5
    velocityY = 0
    gravity_max = -1
    current_breaking_time = 0
    breaking_pozition = Point2d(0,0)
    inventory = Inventory()
    last_player_pos = [0,0,0]
    #section:undefined
    event_list = {"00":"10","01":"11","02":"12"}
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
    #section:screen
    current_frame = pygame.Surface((width, height))
    current_frame.fill("#ccd8ff")
    screen_update = True
    #section:camera
    last_cam_position = None
    cam_moved = [0,0]
    last_position_cam = [0,0]
    angle = 0
    #section:chat
    chat_history = []
    chat_history_timer = []
    chat_history_timer_max_seconds = 10
    chat_line_width = 40
    chat_text_margin = margin(10, 5, 5, 5)
    chat_background_margin = margin(0, 5, 10, 5)
    chat_blur_out_time_seconds = chat_history_timer_max_seconds - 5
    #section:timer
    last_timer_value = 0
    timer = time.time()
    world_auto_save_time_seconds = 120
    timer_start = int(time.time()%world_auto_save_time_seconds)
