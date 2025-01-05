from world_render import get_screen_pos, Point2d, block_size, block_in_screenX, block_in_screenY
from texture_loader import gui_folder, block_names, block_texture_files, not_full_blocks, block_texture_id, list_breaking_time, cursor_folder, texture_folder, sound_folder, music_folder, sound_list, random_sound, load_textures_and_sounds, item_size
from world import Chunk, World, chunk_size_y, chunk_size_x, biomes
# from player import defaultPlayer
from inventory import Inventory
from button import Button
from switch_button import SwitchButton
import file_something.decompression as file_dmp
import file_something.compression as file_cmp
import world_files
import pygame
import sys
import keys
import math
import os
import time
import threading
import gameExceptions
from textinput import TextInput, margin
# import socket_.client as socket_client
# import socket

from main_variables import *

#pygame.display.set_mode((width,height),pygame.locals.RESIZABLE)

def chat_log(*text, recursion = False):
    for i in text:
        if not i:
            continue
        if not recursion:
            i = ">> " + i
        if len(i) > chat_line_width:
            while len(i) > chat_line_width:
                chat_log(i[:chat_line_width], recursion = True)
                i = i[chat_line_width:]
        chat_history_timer.append(timer)
        chat_history.append(i)
def render_chat(screen):
    for i in range(len(chat_history)-1, -1, -1):
        if ((not menus["chat_input_oppened"]) and i < 20) and timer - chat_history_timer[i] >= chat_history_timer_max_seconds:
            #print("chat_history_timer[i]", chat_history_timer[i])
            continue
        elif False and timer - chat_history_timer[i] >= chat_blur_out_time_seconds:
            blur_percentance = chat_blur_out_time_seconds/(timer - chat_history_timer[i])
            text_surface = font.render(str(chat_history[i]), True, (0, 0, 0, int(255*blur_percentance)))
            chat_background_surface = pygame.Surface((text_surface.get_size()[0] + chat_background_margin.left + chat_background_margin.right, text_surface.get_size()[1] + chat_background_margin.top + chat_background_margin.bottom), pygame.SRCALPHA)
            chat_background_surface.fill((0, 0, 0, 255-int(255*blur_percentance)))
            screen.blit(chat_background_surface, (chat_background_margin.left, hotbar_height - 50 - (len(chat_history)-i)*(30 + chat_background_margin.top + chat_background_margin.bottom)))
            screen.blit(text_surface, (chat_text_margin.left, hotbar_height - 50 - (len(chat_history)-i)*(30 + chat_text_margin.top + chat_text_margin.bottom) + chat_text_margin.top))
        else:
            text_surface = font.render(str(chat_history[i]), True, (0, 0, 0))
            chat_background_surface = pygame.Surface((max(text_surface.get_size()[0] + chat_background_margin.left + chat_background_margin.right, 50), text_surface.get_size()[1] + chat_background_margin.top + chat_background_margin.bottom), pygame.SRCALPHA)
            #chat_background_surface = pygame.Surface((350, text_surface.get_size()[1] + chat_background_margin.top + chat_background_margin.bottom), pygame.SRCALPHA)
            chat_background_surface.fill((0, 0, 0, 128))
            screen.blit(chat_background_surface, (chat_background_margin.left, hotbar_height - 50 - (len(chat_history)-i)*(30 + chat_background_margin.top + chat_background_margin.bottom)))
            screen.blit(text_surface, (chat_text_margin.left, hotbar_height - 50 - (len(chat_history)-i)*(30 + chat_text_margin.top + chat_text_margin.bottom) + chat_text_margin.top))
def render_player(player, screen, camera, mouse_x, mouse_y, player_movement_leg_angle, is_game_paused_=False, rotate_player=False)->None:
    """
    This function was optimized by Codeium AI
    Render player in 2D on the screen.

    :param player: Player object to render
    :param screen: Pygame screen object
    :param camera: 2D camera object
    :param mouse_x: Mouse x position
    :param mouse_y: Mouse y position
    :param player_movement_leg_angle: Angle of player leg
    :param is_game_paused_: If game is paused
    :param rotate_player: If player head should be rotated
    """

    # Calculate angle between player and mouse
    mouse_offset_x = mouse_x - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[0]
    mouse_offset_y = mouse_y - get_screen_pos(camera, Point2d(player.x + player.sizex / 2, player.y + player.sizey / 2))[1]
    mouse_offset_y = -mouse_offset_y

    # Calculate player angle
    if not (is_game_paused_) and rotate_player:
        player.angle = math.atan2(mouse_offset_y, mouse_offset_x)

    # Determine which direction the head should face
    if -math.pi/2 < player.angle < math.pi/2:
        head_texture_name = "head_r"
    else:
        head_texture_name = "head_l"

    # Get the head texture
    head_texture = player_textures[head_texture_name]

    # Calculate the offset for the head texture
    original_texture = pygame.transform.scale(head_texture, (block_size*0.5, block_size*0.5))
    if -math.pi/2 < player.angle < math.pi/2:
        offset = pygame.math.Vector2(0, -original_texture.get_height() / 2).rotate(-math.degrees(player.angle))
    else:
        offset = pygame.math.Vector2(0, original_texture.get_height() / 2).rotate(-math.degrees(player.angle))

    # Render the head texture
    body_texture = pygame.transform.rotate(original_texture, math.degrees(player.angle))
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.16, player.y))[0] + offset.x, get_screen_pos(camera, Point2d(player.x, player.y + 0.6))[1] + offset.y))
    screen.blit(body_texture, body_rect)

    # Render the body texture
    body_texture = pygame.transform.scale(player_textures["body"], (block_size*0.3, block_size))
    body_rect = body_texture.get_rect(center=(get_screen_pos(camera, Point2d(player.x - 0.3/2, player.y))[0], get_screen_pos(camera, Point2d(player.x, player.y + 0.1))[1]))
    screen.blit(body_texture, body_rect)

    # Render the leg textures
    leg_texture = player_textures["leg_r"] if -math.pi/2 < player.angle < math.pi/2 else player_textures["leg_l"]
    body_texture = pygame.transform.scale(leg_texture, (block_size * 0.29, block_size * 0.8))
    rotated_texture = pygame.transform.rotate(body_texture, player_movement_leg_angle)
    rotation_point = get_screen_pos(camera, Point2d(player.x - 0.3 / 2, player.y - 0.7))
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(player_movement_leg_angle/2))*block_size*0.29) + player.isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
    rotated_texture = pygame.transform.rotate(body_texture, -player_movement_leg_angle)
    rotated_rect = rotated_texture.get_rect(center=(rotation_point[0] + (math.sin(math.radians(-player_movement_leg_angle/2 + 90))*2*math.sin(math.radians(-player_movement_leg_angle/2))*block_size*0.29) + player.isnegative(player_movement_leg_angle), rotation_point[1]))
    screen.blit(rotated_texture, rotated_rect)
def save_world(filename=None, overwrite = True):
    if current_world_name:
        world_files.save_data({"version":-1,"gamemode":overworld.gamemode,"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite,filename = current_world_name)
        return
    if filename:
        world_files.save_data({"version":-1,"gamemode":overworld.gamemode,"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite, filename = filename)
        return
    world_files.save_data({"version":-1,"gamemode":overworld.gamemode,"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, overwrite=overwrite)
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
    else:
        print(event, type(list(message)), list(message))
        client_dgram.send(event, *message)
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
        case "02":
            overworld.add_player(message[0], float(message[1]), float(message[2]), float(message[3]))
        case "03":
            index = overworld.find_player(message[0])
            overworld.players.pop(index)
            overworld.nicknames.pop(index)
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
            index = overworld.find_player(message[0])
            overworld.players[index].x = float(message[1])
            overworld.players[index].y = float(message[2])
            overworld.players[index].angle = float(message[3])
def connect_to_server_setup(ip, port, nick):
    global overworld, client_sock_stream, nickname, multiplayer_mode, client_dgram
    overworld = World()
    #print("0")
    client_sock_stream = socket_client.SockStreamClient(process_function=message_process)
    #print(0.5)
    client_sock_stream.connect(ip, port, nick)
    #print("1")
    client_dgram = socket_client.DgramClient(process_function=message_process_dgram)
    client_dgram.connect(nick, host=ip, port=port)
    #print(2)
    client_thread_sock_stream = threading.Thread(target=client_sock_stream.receive)
    client_thread_sock_stream.start()
    #print("3")
    client_thread_dgram = threading.Thread(target=client_dgram.receive)
    client_thread_dgram.start()
    nickname = nick
    #print("4")
    multiplayer_mode = True
    client_sock_stream.send("00", nickname, str(0), str(0), str(0))
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
        output.append([biomes.index(type(i.biome)), compress(i.blocks)])
    return output
def parse_world(world):
    output = [[],[]]
    output[0] = parse_chunks(world.chunkpoz)
    output[1] = parse_chunks(world.chunkneg)
    return output
def compress(text):
    #print("!".join(["-".join(list(map(str,i))) for i in text]))
    return file_cmp.compress("!".join(["-".join(list(map(str,i))) for i in text]))
def decompress(text):
    return [list(map(int,i.split("-"))) for i in file_dmp.decompress(text).split("!")]
def load_chunks(chunk_data):
    output = []
    for this_chunk_data in chunk_data:
        this_chunk = Chunk()
        this_chunk.blocks = decompress(this_chunk_data[1])
        this_chunk.biome = biomes[this_chunk_data[0]]()
        output.append(this_chunk)
    return output
def load_world(data):
    global overworld, player, selected_in_hotbar
    overworld = World(not_pregen=True)
    overworld.chunkpoz = load_chunks(data["world"][0])
    overworld.chunkneg = load_chunks(data["world"][1])
    overworld.main_player.x = data["playerx"]
    overworld.main_player.y = data["playery"]
    selected_in_hotbar = data["select_in_hotbar"]
    overworld.gamemode = data["gamemode"]
    overworld.main_player.gamemode = data["gamemode"]
def list_world_files():
    try:
        return os.listdir("./saves/")
    except:
        os.mkdir("./saves/")
        return []
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
        return not_full_blocks[block] 
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
    if Yislegal(y) and world.get_block(x, y) == 0 and (world.get_block(x, y) in not_full_blocks and not entity_here(x, y)):
        
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
    global events, running, mouse_l, t_key_delay, mouse_r_click, mouse_r, selected_in_hotbar, ain_menu_oppened, esc_delay, menus
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
                mouse_r_click = not mouse_r
                mouse_r = True
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
                mouse_r = False
            elif event.button == 3:
                mouse_l = False
        if key_dict[pygame.K_ESCAPE]:
            if not (esc_delay or overworld is None):
                if menus["ingame_main_menu_oppened"]:
                    menus["ingame_main_menu_oppened"] = False
                elif menus["options_menu_oppened"]:
                    menus["options_menu_oppened"] = False
                    menus["ingame_main_menu_oppened"] = True
                elif menus["chat_input_oppened"]:
                    open_menu("None")
                else:
                    menus["ingame_main_menu_oppened"] = True
                esc_delay = True
        elif esc_delay:
            esc_delay = False
        if key_dict[pygame.K_t]:
            if (not menus["chat_input_oppened"]) and (not t_key_delay):
                menus["chat_input_oppened"] = True
                t_key_delay = True
                events[events.index(event)] = pygame.event.Event(pygame.NOEVENT, {})
        elif t_key_delay:
            t_key_delay = False
    if key_dict[pygame.K_F1]:
        global hide_ui
        hide_ui = not hide_ui
        key_dict[pygame.K_F1] = False 
    if key_dict[pygame.K_F3]:
        global debug_mode
        debug_mode = not debug_mode
        debug_mode_switch.current_state = 1 if debug_mode else 0
        key_dict[pygame.K_F3] = False 
    if key_dict[pygame.K_SEMICOLON]:
        running = False
def handle_player_movement():
    global velocityY, player_movement_leg_angle, last_player_pos
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
    if multiplayer_mode and (overworld.main_player.x != last_player_pos[0] or  overworld.main_player.y != last_player_pos[1] or overworld.main_player.angle != last_player_pos[2]):
        send_to_server("00", overworld.main_player.x, overworld.main_player.y, overworld.main_player.angle)
        last_player_pos = [overworld.main_player.x, overworld.main_player.y, overworld.main_player.angle]
def update_camera():
    global camx, camy, camera
    camx = overworld.main_player.x
    camy = overworld.main_player.y
    # camera.x = camx
    # camera.y = camy
    camera.x = camx-(width/(block_size*2)) + ((mouse_x - (width/2))*(mouse_affect))
    camera.y = camy - ((mouse_y - (height/2))*(mouse_affect))
static_screen_size_x = math.ceil(block_in_screenX*1.2)
static_screen_size_y =  math.ceil(block_in_screenY*1.2)
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
                
                    if debug_mode and (base.x+world_x)%chunk_size_x == 0:
                        blockx, blocky, size = staticx + (world_x*block_size), staticy - (world_y*block_size), block_size*1.2
                        current_frame.blit(textures[13], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                        
                except:
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
        #staticy -= height
        print("L", staticx, staticy)
        # print("DUBUG", (camera.x - overworld.main_player.x)*block_size, (camera.y - overworld.main_player.y)*block_size)
        current_frame.fill((0,0,0))
        #print(-cam_moved[0]*block_size, cam_moved[1]*block_size)
        current_frame.blit(last_frame, (-cam_moved[0]*block_size, cam_moved[1]*block_size))
        for world_x in range(static_screen_size_x):
            if cam_moved[1] < 0:
                blockx, blocky, size = staticx + (world_x*block_size), staticy - (block_size), block_size*1.2
                
                #print(blockx, blocky, overworld.get_block(base.x + world_x,base.y))
                current_frame.blit(textures[overworld.get_block(base.x+world_x,base.y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
            
                # blockx, blocky, size = staticx + (world_x*block_size), staticy, block_size*1.2
                # current_frame.blit(textures[overworld.get_block(base.x + world_x,base.y)], (blockx-50, blocky-50), (0, 0, size+block_size_add, size+block_size_add))
            
            else:
                blockx, blocky, size = staticx + (world_x*block_size), staticy - ((static_screen_size_y-1)*block_size), block_size*1.2
                current_frame.blit(textures[overworld.get_block(base.x+world_x,base.y+static_screen_size_y-block_size)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
            
                # blockx, blocky, size = staticx + (world_x*block_size), staticy + ((static_screen_size_y-block_size)), block_size*1.2
                # current_frame.blit(textures[overworld.get_block(base.x + world_x,base.y + ((static_screen_size_y-1)))], (blockx, blocky-600), (0, 0, size+block_size_add, size+block_size_add))
            

        for world_y in range(static_screen_size_y):
            if cam_moved[0] < 0:
                blockx, blocky, size = staticx + block_size, staticy - (world_y*block_size), block_size*1.2
                current_frame.blit(textures[overworld.get_block(base.x,base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                
            else:
                print(blockx, blocky)
                blockx, blocky, size = staticx + ((static_screen_size_x-2)*block_size), staticy - world_y*block_size, block_size*1.2
                current_frame.blit(textures[overworld.get_block(base.x + ((static_screen_size_x-1)),base.y+world_y)], (blockx, blocky), (0, 0, size+block_size_add, size+block_size_add))
                
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
        if multiplayer_mode:
            send_to_server("02", x, y)
        overworld.set_block(cursor_block_x, cursor_block_y, block_texture_id["air"])
def render_cursor():pass
def handle_cursor_and_block_breaking(render_sqare):
    global current_breaking_time, breaking_pozition, cursor_block_x, cursor_block_y, BREAK_BLOCK
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
                BREAK_BLOCK = True
                get_sound(block_names[overworld.getblock(cursor_block_x,cursor_block_y)]).play()
                current_breaking_time = 0
                cursor_texture_id = 0
                #pygame.mixer.Sound("soung.mp3").play()
            cursor_screen_pos = get_screen_pos(camera, Point2d(cursor_block_x, cursor_block_y))
            screen.blit(cursor[cursor_texture_id], (cursor_screen_pos[0], cursor_screen_pos[1]), (0, 0, block_size+1, block_size+1))
        
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
def execute_command(text):
    global overworld, framerate
    if text[0] == "/":
        command = text.split(" ")
        match command[0]:
            case "/tp":
                if len(command) == 3:
                    try:
                        overworld.main_player.x = float(command[1])
                        overworld.main_player.y = float(command[2])
                        return f"Teleporting player to x: {command[1]}, y: {command[2]}"
                    except Exception as e:
                        return f"Invalid coordinates to teleport: {command[1]}, {command[2]}, {e}"
                else:
                    return f"Too few arguments to teleport: {command[1]}, {command[2]}"
            case "/setblock":
                if len(command) == 4:
                    try:
                        overworld.set_block(int(command[1]), int(command[2]), int(command[3]))
                        return f"Set block at x: {command[1]}, y: {command[2]} to {command[3]}"
                    except:
                        return f"Invalid coordinates to set block or invvalid block type: x:{command[1]}, y:{command[2]}, block_type:{command[3]}"
                else:
                    return f"Too few arguments to set block: {command[1]}, {command[2]}"
            case "/setslot":
                if len(command) == 3:
                    try:
                        inventory.set_slot(int(command[1]), 0, int(command[2]))
                        return f"Set hotbar slot {command[1]} to {command[2]}"
                    except:
                        return f"Invalid slot or invvalid block type: {command[1]}, {command[2]}"
                else:
                    return f"Too few arguments to set hotbar slot: {command[1]}, {command[2]}"
            case "/crash":
                save_world()
                raise Exception("Crash command executed")
            case "/fps":
                try:
                    if len(command) == 2:
                        if command[1] == "d" or command[1] == "default":
                            framerate = defaultFramerate
                            return f"Setting framerate to default: {defaultFramerate}"
                        if int(command[1]) > 2:
                            framerate = int(command[1])
                        else:
                            return f"Too low framerate: {command[1]}, requied 3 or more."
                    else:
                        return "Too few arguments."
                except Exception as e:
                    return f"Error while processing message: {e}"
            case _:
                return f"Unknown command: {command[0]}"
    else:
        return text
def render_ui(cursor_block_x:int, cursor_block_y:int):
    coordinates_text = f"X: {overworld.main_player.x:.2f}, Y: {overworld.main_player.y:.2f}"
    text_surface = font.render(coordinates_text, True, ui_colour)
    screen.blit(text_surface, (10, 10))

    fps = clock.get_fps()
    fps_text = f"FPS: {fps:.2f}"
    fps_surface = font.render(fps_text, True, ui_colour)
    screen.blit(fps_surface, (10, 50))
    if debug_mode and len(overworld.chunkpoz) + len(overworld.chunkneg) > 0:
        debug_text = f"Debug: \nBiome: {type(overworld.get_chunk(overworld.main_player.x//chunk_size_x).biome)}\nMaxFps: {defaultFramerate}"
        y_offset = 80
        for line in debug_text.split('\n'):
            debug_surface = font.render(line, True, ui_colour)
            screen.blit(debug_surface, (10, y_offset))
            y_offset += 30  

    screen.blit(gui_textures["hotbar"], [hotbar_positions[0], height - 90])
    for i in range(9):
        item = inventory.get_slot(i, 0)
        if item != None:
            try:
                screen.blit(item_textures[block_texture_id[item]], [hotbar_positions[i] + 8 - (item_size/2*0) + ((block_size - item_size)/8), hotbar_height])
            except Exception as e:
                print("Error: (probably item is not loaded :D) |", e)
                print("Quitting!")
                global running
                running = False
    if overworld.main_player.gamemode == 1:
        screen.blit(health_bar_textures[f"health{overworld.main_player.health}"], [hotbar_positions[0], hotbar_height - 48])
    screen.blit(gui_textures["selected"], [hotbar_positions[selected_in_hotbar] - 4, height - 90 - 4])
    render_chat(screen)
    
def set_world(world):
    global overworld
    overworld = world
def check_gui_interaction():
    global overworld, multiplayer_mode, player, mouse_x, mouse_y, running, menus, mouse_r_click, update_frame_once, current_world_name, debug_mode

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if menus["ingame_main_menu_oppened"]:
        if back_button.is_pressed:
            open_menu(None)
        if quit_button.is_pressed:
            if multiplayer_mode:
                multiplayer_mode = False
                client_sock_stream.close()
                client_dgram.close()
            else:
                save_world(overwrite=True)
            overworld = None
            open_menu("main_menu_oppened")
        if save_world_button.is_pressed and not multiplayer_mode:
            #open_menu("menus["create_world_menu_oppened"]")
            save_world(overwrite=True)
            #world_files.save_data({"version":-1,"gamemode":overworld.gamemode, "playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)})
        if options_button.is_pressed:
            open_menu("options_menu_oppened")
    elif menus["main_menu_oppened"]:
        if quit_button.is_pressed:
            running = False
        if new_world_button.is_pressed:
            open_menu("create_world_menu_oppened", notraise=True)
        if load_world_button.is_pressed:
            open_menu("open_world_menu_oppened")
    elif menus["options_menu_oppened"]:
        x = debug_mode_switch.current_state==1
        debug_mode = x
        if done_back_to_main_button.is_pressed:
            open_menu("ingame_main_menu_oppened")
    elif menus["create_world_menu_oppened"]:
        name = world_name_input.text
        if done_back_to_main_button.is_pressed:
            if name != "":
                world_name_input.placeholder = "World name"
                world_name_input.text = ""
                overworld = World()
                overworld.gamemode = game_mode_switch.getstate()
                save_world(filename=name, overwrite=False)
                #world_files.save_data({"version":-1,"gamemode":str(overworld.gamemode),"playerx":overworld.main_player.x, "playery":overworld.main_player.y, "select_in_hotbar":selected_in_hotbar , "world":parse_world(overworld)}, filename=name)
                open_menu(None)
                pygame.mouse.set_pos(width // 2, height // 2)
            else:
                world_name_input.placeholder = "Please enter"
        if back_button.is_pressed:
            world_name_input.placeholder = "World name"
            world_name_input.text = ""
            open_menu("main_menu_oppened")
    elif menus["file_menu_oppened"]:
        if save_world_button.is_pressed:
            if current_world_name == None:
                save_world(overwrite=False)
            else:
                save_world(filename=current_world_name, overwrite=True)
        elif load_world_button.is_pressed:
            open_menu("open_world_menu_oppened")
        elif done_back_to_main_button.is_pressed:
            open_menu("ingame_main_menu_oppened")
    elif menus["multiplayer_menu_oppened"]:
        if done_back_to_main_button.is_pressed:
            server_address = server_ip_input.text
            nickname = nickname_input.text
            global server_ip
            print("Server IP:", server_ip_input.text)
            server_ip = server_address
            try:
                global client
                try:
                    client = connect_to_server_setup(server_ip.split(":")[0], int(server_ip.split(":")[1]), nickname)
                except Exception as e:
                    print("Error connecting to server: ", e, ";-")
                    raise gameExceptions.FailedConnectingServer
                open_menu(None)
                print("Connected to server")
            except gameExceptions.FailedConnectingServer as e:
                print("Error connecting server: ", e, ";")
            #print("Back to main menu")
        if back_button.is_pressed:
            open_menu("main_menu_oppened")
    elif menus["open_world_menu_oppened"]:
        if done_back_to_main_button.is_pressed:
            open_menu("main_menu_oppened")
        world_files_list = list_world_files()
        for i in range(len(world_files_list)):
            try:
                if world_files_list[i][-5:] != ".json":
                    continue
            except:
                continue
            if i > 4:
                if load_world_button.is_pressed:
                    try:
                        print("Loading world: ", world_files_list[i])
                        load_world(world_files.load_data(world_files_list[i]))
                        current_world_name = world_files_list[i]
                        menus["main_menu_oppened"] = False
                        menus["open_world_menu_oppened"] = False
                        if not menus["main_menu_oppened"]:
                            update_frame_once = True
                        pygame.mouse.set_pos([width/2,height/2])
                    except:
                        print("Error loading world", world_files_list[i])
            else:
                if load_world_button.is_pressed:
                    print("Loading world: ", world_files_list[i])
                    try:
                        load_world(world_files.load_data(world_files_list[i]))
                        current_world_name = world_files_list[i]
                        menus["main_menu_oppened"] = False
                        menus["open_world_menu_oppened"] = False
                        if not menus["main_menu_oppened"]:
                            update_frame_once = True
                        pygame.mouse.set_pos([width/2,height/2])
                    except:
                        print("Error loading world", world_files_list[i])
    elif menus["chat_input_oppened"]:
        chat_input.active = True
        text = chat_input.text
        if text:
            chat_log(execute_command(text))
            chat_input.text = ""
            open_menu("None")
        elif text == "":
            open_menu("None")
def render_gui():

    global overworld, multiplayer_mode, player, mouse_x, mouse_y, running, menus, mouse_r_click, update_frame_once, current_world_name, debug_mode

    if menus["ingame_main_menu_oppened"]:
        overall = pygame.Surface((width, height), pygame.SRCALPHA)
        overall.fill((0, 0, 0, 200))
        screen.blit(overall, (0, 0))
        back_button.render(screen, mouse_r_click)
        quit_button.render(screen, mouse_r_click)
        save_world_button.render(screen, mouse_r_click, text="Save")
        options_button.render(screen, mouse_r_click)
    elif menus["main_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        #COMING SOON
        # if multiplayer_menu_button.render(screen, mouse_r_click):
        #     open_menu("multiplayer_menu_oppened")  #TODO - work in progress :D
        quit_button.render(screen, mouse_r_click)
        new_world_button.render(screen, mouse_r_click)
        load_world_button.render(screen, mouse_r_click, y=340, width=400)
    elif menus["options_menu_oppened"]:
        overall = pygame.Surface((width, height), pygame.SRCALPHA)
        overall.fill((0, 0, 0, 200))
        screen.blit(overall, (0, 0))
        debug_mode_switch.render(screen, mouse_r_click)
        done_back_to_main_button.render(screen, mouse_r_click)
    elif menus["create_world_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        world_name_input.render(screen, events, [mouse_x, mouse_y, mouse_r_click], return_text=True)
        game_mode_switch.render(screen, mouse_r_click)[1]
        done_back_to_main_button.render(screen, mouse_r_click, x=width // 2 + 10, width=190)
        back_button.render(screen, mouse_r_click, x=width // 2 - 200, width=190, y=height - 200, text="Back")
    elif menus["file_menu_oppened"]:
        save_world_button.render(screen, mouse_r_click)
        load_world_button.render(screen, mouse_r_click)
        update_world_button.render(screen, mouse_r_click)
        done_back_to_main_button.render(screen, mouse_r_click)
    elif menus["multiplayer_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        server_ip_input.render(screen, events, return_text=True, collision = [mouse_x, mouse_y, mouse_r_click])
        nickname_input.render(screen, events, return_text=True, collision = [mouse_x, mouse_y, mouse_r_click])
        done_back_to_main_button.render(screen, mouse_r_click, width=190, x=400)
        back_button.render(screen, mouse_r_click, text="Cancel", width=190, x=200, y=height - 200)
    elif menus["open_world_menu_oppened"]:
        screen.blit(gui_textures["main_manu_background"], [0,0])
        done_back_to_main_button.render(screen,mouse_r_click)
        world_files_list = list_world_files()
        for i in range(len(world_files_list)):
            try:
                if world_files_list[i][-5:] != ".json":
                    continue
            except:
                continue
            if i > 4:
                if load_world_button.render(screen, mouse_r_click, x=width // 2 + 10, y = (i-5)*70 + 50, text = world_files_list[i]):
                    try:
                        print("Loading world: ", world_files_list[i])
                        load_world(world_files.load_data(world_files_list[i]))
                        current_world_name = world_files_list[i]
                        menus["main_menu_oppened"] = False
                        menus["open_world_menu_oppened"] = False
                        if not menus["main_menu_oppened"]:
                            update_frame_once = True
                        pygame.mouse.set_pos([width/2,height/2])
                    except:
                        print("Error loading world", world_files_list[i])
            else:
                if load_world_button.render(screen, mouse_r_click, y = i*70 + 50, text = world_files_list[i]):
                    print("Loading world: ", world_files_list[i])
                    try:
                        load_world(world_files.load_data(world_files_list[i]))
                        current_world_name = world_files_list[i]
                        menus["main_menu_oppened"] = False
                        menus["open_world_menu_oppened"] = False
                        if not menus["main_menu_oppened"]:
                            update_frame_once = True
                        pygame.mouse.set_pos([width/2,height/2])
                    except:
                        print("Error loading world", world_files_list[i])
    elif menus["update_world_menu_oppened"]:
        raise gameExceptions.MenuNotExist
    elif menus["chat_input_oppened"]:
        chat_input.render(screen, events, [mouse_x, mouse_y, mouse_r_click])
def check_timer():
    
    global last_timer_value, timer
    last_timer_value = timer
    timer = time.time()

    if overworld and (not multiplayer_mode) and int(timer + timer_start) % world_auto_save_time_seconds == 0 and int(timer) != int(last_timer_value):
        save_world(filename=current_world_name, overwrite=True)
        print("Auto saving world.")
        chat_log("Auto saved world.")

    # if int(timer) % 5 == 0 and int(timer) != int(last_timer_value):
    #     chat_log("Time: " + str(int(timer)) + " seconds")

"""--------------------------- MAIN GAME LOOP ----------------------------------------------------------------"""
def run():
    global tick
    TPS = 30
    TICK_DEFAULT_WAITING_TIME = 1/TPS
    GUI_TPS = 30
    GUI_TICK_DEFAULT_WAITING_TIME = 1/GUI_TPS
    def TICK_THREAT():
        global events, overworld, BREAK_BLOCK, phase, mouse_r_click
        LAST_TICK = -1
        GUI_LAST_TICK = -1
        while running:
            time_ = time.time()
            if time_ - GUI_LAST_TICK > GUI_TICK_DEFAULT_WAITING_TIME:
                handle_events()
                check_gui_interaction()
                GUI_LAST_TICK = time_
            if time_ - LAST_TICK > TICK_DEFAULT_WAITING_TIME:
                if not (menus["create_world_menu_oppened"] or menus["open_world_menu_oppened"] or menus["update_world_menu_oppened"] or menus["main_menu_oppened"] or menus["multiplayer_menu_oppened"]):
                    handle_player_movement()
                    if BREAK_BLOCK:
                        break_block(cursor_block_x, cursor_block_y)
                        BREAK_BLOCK = False
                    if mouse_r:
                        try:
                            try_place_block(overworld, cursor_block_x, cursor_block_y, block_texture_id[inventory.get_slot(selected_in_hotbar, 0)])
                        except:
                            pass
                LAST_TICK = time_
            time.sleep(min(GUI_TICK_DEFAULT_WAITING_TIME, TICK_DEFAULT_WAITING_TIME)/10)


    TICK_THREAD_ = threading.Thread(target=TICK_THREAT)
    TICK_THREAD_.start()
    while running:
        if not (menus["create_world_menu_oppened"] or menus["open_world_menu_oppened"] or menus["update_world_menu_oppened"] or menus["main_menu_oppened"] or menus["multiplayer_menu_oppened"]):
            update_camera()
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

        tick = ((tick+1) % framerate)
        check_timer()
        clock.tick(framerate)
    if multiplayer_mode:
        client_sock_stream.close()
        client_dgram.close()
    pygame.quit()
    sys.exit()
    exit(1)

if __name__ == "__main__":
    run()