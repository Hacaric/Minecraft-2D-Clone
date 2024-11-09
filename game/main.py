from world_render import get_screen_pos, Point2d, block_size, block_in_screenX, block_in_screenY
from texture_storage import player_textures, gui_textures, gui_folder, block_names, block_texture_files, not_full, block_texture_id, list_breaking_time, cursor_folder, texture_folder, sound_folder, music_folder, sound_list, random_sound, load_textures_and_sounds, item_size
from world import Chunk, World, chunk_size_y, chunk_size_x
from player import defaultPlayer
from inventory import Inventory
from button import Button
import world_files
import pygame
import sys
import keys
import math
import os
import time
running = True
# Initialize Pygame
pygame.init()

# Set up the display 
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Paper minecraft - indev")
#pygame.display.set_mode((width,height),pygame.locals.RESIZABLE)
block_size_add = 1

cursor, textures, block_sounds, item_textures = load_textures_and_sounds(block_size, block_size_add)
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

overworld = World()

current_world_name = None
update_frame_once = True
tick = 0
movement_speed = 64/400#block_size/156#
movement_detail = 64/4
player_movement_leg_angle = 0

main_menu_oppened = True
main_menu_gui_oppened = False
options_menu_oppened = False
file_menu_opened = False
open_world_menu_oppened = False
update_world_menu_oppened = False
esc_delay = False
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



#--------PLAYER SETUP-----------
# Player setup
player_sizex = 0.3
player_sizey = 2
player = defaultPlayer(overworld, 0, player_sizex, player_sizey, player_textures, block_size)
player_color = (0, 20, 255)  # Gray color
gravity = 0.05
jump_affect = 0.5
velocityY = 0
gravity_max = -1
#-----------PLAYER SETUP END------------

current_breaking_time = 0
breaking_pozition = Point2d(0,0)

inventory = Inventory()

def open_menu(menu:str, all_other_false = True, disable_mouse_click = True):
    global main_menu_oppened, file_menu_opened, main_menu_gui_oppened, options_menu_oppened, open_world_menu_oppened, update_world_menu_oppened
    if menu == "main_menu_oppened":
        main_menu_oppened = True
    elif menu == "file_menu_opened":
        file_menu_opened = True
    elif menu == "main_menu_gui_oppened":
        main_menu_gui_oppened = True
    elif menu == "options_menu_oppened":
        options_menu_oppened = True
    elif menu == "open_world_menu_oppened":
        open_world_menu_oppened = True
    elif menu == "update_world_menu_oppened":
        update_world_menu_oppened = True
    if all_other_false:
        for menu_name in ["main_menu_oppened", "file_menu_opened", "main_menu_gui_oppened", "options_menu_oppened", "open_world_menu_oppened", "update_world_menu_oppened"]:
            if menu_name != menu:
                globals()[menu_name] = False 
    if disable_mouse_click:
        global mouse_r_click
        mouse_r_click = False
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
    overworld.chunkpoz = load_chunk(data["world"][0])
    overworld.chunkneg = load_chunk(data["world"][1])
    player.x = data["playerx"]
    player.y = data["playery"]
    selected_in_hotbar = data["select_in_hotbar"]
def list_world_files():
    return os.listdir("saves")
def is_game_paused():
    return (main_menu_oppened or file_menu_opened or main_menu_gui_oppened or options_menu_oppened or open_world_menu_oppened or update_world_menu_oppened)

def get_sound(block_name):
    return random_sound(block_name, block_sounds)
    try:
        return block_sound[block_texture_id[block_name]]
    except:
        print("Error finding sound")
        return block_sound[0]#error_sound

#--------UTILITY FUNCTIONS-----------
def get_cursor_state(block_id, breaking_time):
    if player.gamemode == 0 and breaking_time >= 1:
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
    corners = player.corners()
    return True in [((math.floor(corners[i][0])==x)and(math.floor(corners[i][1])==y)) for i in range(4)]

def isfree(x, y, entitywidth, entityheight):
    #    return(not (False in [movable(get_block(x, y)), movable(get_block(x + entitywidth, y)), movable(get_block(x, y + entityheight)), movable(get_block(x + entitywidth, y + entityheight))]))        

    for check_x in range(math.floor(x), math.ceil(x + entitywidth)):
        for check_y in range(math.floor(y), math.ceil(y + entityheight)):
            if not movable(get_block(check_x, check_y)):
                return False
    return True
def on_ground(playerx, playery):
    return not isfree(playerx, playery - 0.1, player.sizex, player.sizey)

def Yislegal(y):
    return 0 < y < chunk_size_y
#-----------UTILITY FUNCTIONS END------------

#--------BLOCK PLACEMENT-----------
last_placed_tick = -1
placement_delay = 1
def try_place_block(world, x, y, id):
    if Yislegal(y) and world.get_block(x, y) == 0 and (world.get_block(x, y) in not_full or not entity_here(x, y)):
        world.set_block(x, y, id)
        # if world.current_delay == 0:
        #     world.current_delay = world.block_sound_delay
        get_sound(block_names[id]).play()
#-----------BLOCK PLACEMENT END------------

# Initialize font
font = pygame.font.Font(None, 36)

# FPS counter setup
clock = pygame.time.Clock()

# Mouse button states
mouse_l = False
mouse_r = False
mouse_r_click = False

#preloaded_area = overworld.loaded_chunks

def handle_events():
    global running, mouse_l, mouse_r_click, mouse_r, selected_in_hotbar, main_menu_gui_oppened, esc_delay, options_menu_oppened
    for event in pygame.event.get():
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
                # if main_menu_gui_oppened:
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
                if main_menu_gui_oppened:
                    main_menu_gui_oppened = False
                elif options_menu_oppened:
                    options_menu_oppened = False
                    main_menu_gui_oppened = True
                else:
                    main_menu_gui_oppened = True
                esc_delay = True
        else:
            esc_delay = False
    if key_dict[pygame.K_SEMICOLON]:
        running = False

def handle_player_movement():
    global velocityY, player_movement_leg_angle
    last_player_x = player.x
    if key_dict[pygame.K_a]:
        if isfree(player.x - movement_speed, player.y, player.sizex, player.sizey):
            player.x -= movement_speed
        elif isfree(player.x - movement_speed/movement_detail, player.y, player.sizex, player.sizey):
            player.x -= movement_speed/movement_detail
    if key_dict[pygame.K_d]:
        if isfree(player.x + movement_speed, player.y, player.sizex, player.sizey):
            player.x += movement_speed
        elif isfree(player.x + movement_speed/movement_detail, player.y, player.sizex, player.sizey):
            player.x += movement_speed/movement_detail
    if key_dict[pygame.K_s]:
        if isfree(player.x, player.y - movement_speed, player.sizex, player.sizey):
            player.y -= movement_speed
        elif isfree(player.x, player.y - movement_speed/movement_detail, player.sizex, player.sizey):
            player.y -= movement_speed/movement_detail
    if player.x - last_player_x == 0:
        player_movement_leg_angle = round((player_movement_leg_angle)/2)
        #print("NOOO")
    else:
        #print(last_player_x - player.x)
        player_movement_leg_angle = (((last_player_x - player.x)*80 + 45) + player_movement_leg_angle) % 90 - 45
        if player_movement_leg_angle < 90:
            player_movement_leg_angle = player_movement_leg_angle
        #print(player_movement_leg_angle)
    if not isfree(player.x, player.y, player.sizex, player.sizey):
        player.damage(0)
        player.y += 0
    if True:
        if on_ground(player.x, player.y):
            if key_dict[pygame.K_w]:
                velocityY = jump_affect
            else:
                velocityY = 0
        else:
            velocityY += (gravity_max-velocityY)*gravity
        if not isfree(player.x, player.y+velocityY, player.sizex, player.sizey):
            velocityY = velocityY/2
        velocityY = round(velocityY, 2)
        if isfree(player.x, player.y + velocityY, player.sizex, player.sizey):
            player.y += velocityY
    if player.y < -10:
        player.damage(1)

def update_camera():
    global camx, camy, camera
    camx = player.x
    camy = player.y
    camera.x = camx
    camera.y = camy
    mouse_x, mouse_y = pygame.mouse.get_pos()
    camera.x = camx-(width/(block_size*2)) + ((mouse_x - (width/2))*(mouse_affect))
    camera.y = camy - ((mouse_y - (height/2))*(mouse_affect))

def render_world():
    screen.fill(overworld.background)
    base = Point2d(int(camera.x) - 1, int(camera.y - block_in_screenY/2))
    staticx, staticy = get_screen_pos(camera, Point2d(base.x, base.y))[:2]
    # #print(int(staticx + block_size), int(staticy + block_size))

    # --- OLD RENDERING ---
    # position_list = [[],[]]

    # for world_x in range(math.ceil(block_in_screenX * 1.2)):
    #     p = get_screen_pos(camera, Point2d(base.x+world_x, 0))
    #     position_list[0].append(p[0])
    # for world_y in range(math.ceil(block_in_screenY * 1.2)):
    #     p = get_screen_pos(camera, Point2d(0, base.y+world_y))
    #     position_list[1].append(p[1])


    # print("p", position_list[0][1], position_list[1][1], overworld.get_block(base.x+world_x,base.y+world_y))
    for world_x in range(math.ceil(block_in_screenX * 1.2)):
        for world_y in range(math.ceil(block_in_screenY * 1.2)):
            try:
                blockx, blocky, size = staticx + (world_x*block_size), staticy - (world_y*block_size), block_size*1.2 #get_screen_pos(camera, Point2d(base.x+world_x, base.y+world_y))
                #print("BBB", blockx, blocky, size)
                screen.blit(textures[overworld.get_block(base.x+world_x,base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
            except:
                pass
# ---- OLD RENDERING ----
# def render_world():
#     global position_list
#     screen.fill(overworld.background)
#     #if player.x_change > 10 or player.y_change > 10:
#     base = Point2d(int(camera.x) - 1, int(camera.y - block_in_screenY/2))
#     #print(base.x, base.y)
#     try:
#         #""+0
#         position_list
#     except Exception as e:
#         #Create grid for blocksto fit into screen if it doesnt exist
#         print("generating pattern :D", player.x, e)
#         position_list = [[],[]]
#         for world_x in range(math.ceil(block_in_screenX * 1.2)):
#             p = get_screen_pos(Point2d(0, 0), Point2d(base.x+world_x, 0))
#             position_list[0].append(p[0])
#         for world_y in range(math.ceil(block_in_screenY * 1.2)):
#             p = get_screen_pos(Point2d(0, 0), Point2d(0, base.y+world_y))
#             position_list[1].append(p[1])
#         print(position_list[0][0])
    
#     offset = get_screen_pos(camera, Point2d(0,0))
#     offset[0] %= block_size
#     offset[1] %= block_size

#     for world_x in range(math.ceil(block_in_screenX * 1.2)):
#         for world_y in range(math.ceil(block_in_screenY * 1.2)):
#             try:
#                 blockx, blocky, size = position_list[0][world_x] - ((camera.x)*block_size), position_list[1][world_y] + ((camera.y)*block_size), block_size*1.2 #get_screen_pos(camera, Point2d(base.x+world_x, base.y+world_y))
#                 #print(blockx, blocky, overworld.get_block(base.x+world_x,base.y+world_y))
#                 #print(blockx, blocky, size)
#                 #print(blockx, blocky)
#                 screen.blit(textures[overworld.get_block(base.x+world_x,base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
#             except:
#                 print("something went worng - block does not exist")
#                 pass
def isnegative(x):
    if x < 0:
        return -1
    return 1
angle = 0
def render_player():
    global angle
    
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate angle between player and mouse
    dx = mouse_x - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[0]
    dy = mouse_y - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[1]
    dy = -dy
    if not (is_game_paused()):
        angle = math.atan2(dy, dx)
    #print(math.degrees(angle))
    if -math.pi/2 < angle < math.pi/2:
        t = "head_r"
    else:
        t = "head_l"
    original_texture = pygame.transform.scale(player_textures[t], (block_size*0.5, block_size*0.5))
    body_texture = pygame.transform.rotate(original_texture, math.degrees(angle))

    if -math.pi/2 < angle < math.pi/2:
        offset = pygame.math.Vector2(0, -original_texture.get_height() / 2).rotate(-math.degrees(angle))
    else:
        offset = pygame.math.Vector2(0, original_texture.get_height() / 2).rotate(-math.degrees(angle))
    #print(angle)
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.16, player.y))[0] + offset.x, get_screen_pos(camera, Point2d(player.x, player.y + 0.6))[1] + offset.y))
    screen.blit(body_texture, body_rect)
    if -math.pi/2 < angle < math.pi/2:
        leg_texture = player_textures["leg_l"]
    else:
        leg_texture = player_textures["leg_r"]
    body_texture = pygame.transform.scale(player_textures["body"], (block_size*0.3, block_size))
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.3/2, player.y))[0], get_screen_pos(camera, Point2d(player.x, player.y + 0.1))[1]))
    screen.blit(body_texture, body_rect)
    body_texture = pygame.transform.scale(leg_texture, (block_size * 0.29, block_size * 0.8))
    rotated_texture = pygame.transform.rotate(body_texture, player_movement_leg_angle)
    rotation_point = get_screen_pos(camera, Point2d(player.x - 0.3 / 2, player.y - 0.7))
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(player_movement_leg_angle/2))*block_size*0.29) + isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
    body_texture = pygame.transform.scale(leg_texture, (block_size * 0.29, block_size * 0.8))
    rotated_texture = pygame.transform.rotate(body_texture, -player_movement_leg_angle)
    rotation_point = get_screen_pos(camera, Point2d(player.x - 0.3 / 2, player.y - 0.7))
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(-player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(-player_movement_leg_angle/2))*block_size*0.29) + isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
    # player.render(screen, get_screen_pos(camera, Point2d(camx, camy))[0], get_screen_pos(camera, Point2d(camx, camy))[1])
    # player_screen_pos = get_screen_pos(camera, Point2d(camx, camy))
    # pygame.draw.rect(screen, player.colour, (player_screen_pos[0], player_screen_pos[1]-block_size, (player.sizex + 0.1)*block_size, (player.sizey + 0.1)* block_size))
    # screen.blit(textures[5], (player_screen_pos[0], player_screen_pos[1]+player.sizey), (0, 0, block_size/2,block_size/2))
def handle_cursor(render_sqare):
    global current_breaking_time, breaking_pozition, options_menu_oppened, main_menu_gui_oppened
    #print(main_menu_gui_oppened)
    if main_menu_gui_oppened:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif options_menu_oppened:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    if not render_sqare:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor_block_x = math.floor(camera.x + (mouse_x) / block_size)
        cursor_block_y = math.floor(camera.y - (mouse_y - height/2) / block_size) + 1
        cursor_texture_id = get_cursor_state(get_block(cursor_block_x, cursor_block_y), current_breaking_time)
        pointing_at_block = overworld.get_block(cursor_block_x, cursor_block_y)
        if cursor_texture_id >= 0:
            if cursor_texture_id == 100:
                if overworld.get_block(cursor_block_x, cursor_block_y) != block_texture_id["air"]:
                    get_sound(block_names[pointing_at_block]).play()
                    overworld.set_block(cursor_block_x, cursor_block_y, block_texture_id["air"])
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
            if (overworld.current_delay == 0 and pointing_at_block != 0):
                overworld.current_delay = overworld.block_sound_delay 
                get_sound(block_names[pointing_at_block]).play()
        else:
            current_breaking_time = 0
            breaking_pozition.x = cursor_block_x
            breaking_pozition.y = cursor_block_y
        
        return cursor_block_x, cursor_block_y
    else:
        return 0, 0

def render_ui(cursor_block_x, cursor_block_y):
    coordinates_text = f"X: {player.x:.2f}, Y: {player.y:.2f}, Helath: {player.health}, Entity: {entity_here(cursor_block_x, cursor_block_y)}  Mousel {mouse_l}, [cam.x:{camera.x*block_size}]"
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
    global running, main_menu_gui_oppened, options_menu_oppened, file_menu_opened, mouse_r_click, open_world_menu_oppened, update_world_menu_oppened, update_frame_once, current_world_name, main_menu_oppened, overworld
    
    if main_menu_gui_oppened:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))  # Add a semi-transparent black overlay
        if quit_button.render(screen, mouse_r_click):
            open_menu("main_menu_oppened")
        # if back_button.render(screen, mouse_r_click):
        #     open_menu("main_menu_oppened")
        # if main_menu_gui_oppened:
        #     options_menu_oppened = False
        #     file_menu_opened = False
        if options_button.render(screen, mouse_r_click):
            open_menu("options_menu_oppened")
        if file_options_button.render(screen, mouse_r_click):
            open_menu("file_menu_opened")

    if main_menu_oppened and not open_world_menu_oppened:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        if quit_button.render(screen, mouse_r_click):
            running = False
        if new_world_button.render(screen, mouse_r_click):
            overworld = World()
            open_menu("None")
        if load_world_button.render(screen, mouse_r_click, y=340, width=400):
            open_menu("open_world_menu_oppened")
            main_menu_oppened = True
    if options_menu_oppened:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))  # Add a semi-transparent black overlay
        if done_back_to_main_button.render(screen, mouse_r_click):
            open_menu("main_menu_gui_oppened")

    if file_menu_opened:
        if save_world_button.render(screen, mouse_r_click):
            if current_world_name == None:
                world_files.save_data({"version":-1,"playerx":player.x, "playery":player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)})
            else:
                world_files.save_data({"version":-1,"playerx":player.x, "playery":player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=current_world_name, filetype="", overwrite=True)
            #print("World saved")
        elif load_world_button.render(screen, mouse_r_click):
            open_menu("open_world_menu_oppened")
        elif False and update_world_button.render(screen, mouse_r_click):
            open_menu("update_world_menu_oppened")
            #load_world(world_files.load_data("new_world_button.json"))
        elif done_back_to_main_button.render(screen, mouse_r_click):
            open_menu("main_menu_gui_oppened")

    if open_world_menu_oppened:
        if main_menu_oppened:
            screen.blit(gui_textures["main_manu_background"], [0,0])
        else:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        if done_back_to_main_button.render(screen,mouse_r_click):
            if main_menu_oppened:
                open_menu("main_menu_oppened")
            else:
                open_menu("file_menu_opened")
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
                    main_menu_oppened = False
                    open_world_menu_oppened = False
                    if not main_menu_oppened:
                        update_frame_once = True
            else:
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 50, text = world_files_list[i]):
                    print("Loading world: ", world_files_list[i])
                    load_world(world_files.load_data(world_files_list[i]))
                    current_world_name = world_files_list[i]
                    main_menu_oppened = False
                    open_world_menu_oppened = False
                    if not main_menu_oppened:
                        update_frame_once = True

    if update_world_menu_oppened:
        if done_back_to_main_button.render(screen,mouse_r_click):
            update_world_menu_oppened = False
            file_menu_opened = True
        world_files_list = list_world_files()#current_world_name
        if not current_breaking_time:
            if load_world_button.render(screen, mouse_r_click, y = 50, text = f"Current: {current_world_name}"[:21]+".."):
                world_files.save_data({"version":-1,"playerx":player.x, "playery":player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=current_world_name, overwrite=True)

            for i in range(len(world_files_list)):
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 120, text = world_files_list[i]):
                    world_files.save_data({"version":-1,"playerx":player.x, "playery":player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=world_files_list[i], overwrite=True)
        else:            
            for i in range(len(world_files_list)):
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 50, text = world_files_list[i]):
                    world_files.save_data({"version":-1,"playerx":player.x, "playery":player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=world_files_list[i], overwrite=True)
  





"""--------------------------- MAIN GAME LOOP ----------------------------------------------------------------"""
#--------MAIN GAME LOOP-----------
# # Main game loop
# from textinput import Input as xdddinput
# inputtext = xdddinput(0, 0, 300, 50, gui_textures["button"], text="ahoj:D")
while running:
    # print("open_world_menu_oppened:", open_world_menu_oppened)
    # print("main_menu_oppened:", main_menu_oppened)
    # print("update_world_menu_oppened:", update_world_menu_oppened)
    # print("file_menu_opened:", file_menu_opened)
    # print("main_menu_gui:", main_menu_gui_oppened)
    #print(player.x)
    handle_events()
    if not main_menu_oppened:
        # print(overworld.get_chunk(round(player.x)//chunk_size_x).surface(round(player.x)%chunk_size_x))
        # print("X",player.x)
        if update_frame_once or not (is_game_paused()):
            handle_player_movement()
            update_camera()
            update_frame_once = False
        #overworld.check_preloaded(player.x//16, player.x)
        render_world()
        render_player()
        cursor_block_x, cursor_block_y = handle_cursor(is_game_paused())
        render_ui(cursor_block_x, cursor_block_y)
    render_gui()
    # print(inputtext.render(screen))

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    overworld.current_delay = max(0, overworld.current_delay-1)
    tick += 1
    clock.tick(30)
    mouse_r_click = False
#-----------MAIN GAME LOOP END------------

# Quit Pygame
pygame.quit()
sys.exit()
