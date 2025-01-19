import pygame
import random
import gameExceptions
import os

# Texture and sound data
#block_names = ["air", "sand", "cobblestone", "stone", "bedrock", "grass", "dirt", "plank", "glass", "wood", "leaves", "short_grass"]
block_texture_files = {
    "air": ["#.png"],                          # 0
    "sand": ["sand.png"],                    # 1
    "cobblestone": ["Cobblestone.png"],      # 2
    "stone": ["rock.png"],                   # 3
    "bedrock": ["bedrock.png"],              # 4
    "grass": ["grass.png"],                  # 5
    "dirt": ["dirt.png"],                    # 6
    "plank": ["woodenplanks.png"],           # 7
    "glass": ["glass2.png"],                 # 8
    "wood":["wood.png"],                     # 9
    "leaves":["leaves2.png"],                # 10
    "short_grass":["short_grass.png"],       # 11
    "flower":["rose3.png"],                  # 12
    "chunk_border":["chunk_border.png"],     # 13
}
block_names = []
for item in block_texture_files:
    block_names.append(item)
#item_names = ["air", "sand", "cobblestone", "stone", "bedrock", "grass", "dirt", "plank", "glass", "wood", "leaves"]
item_texture_names = {
    "air": ["#.png"],                    # 0
    "sand": ["sand.png"],              # 1
    "cobblestone": ["Cobblestone.png"], # 2
    "stone": ["rock.png"],             # 3
    "bedrock": ["bedrock.png"],        # 4
    "grass": ["grass.png"],            # 5
    "dirt": ["dirt.png"],              # 6
    "plank": ["woodenplanks.png"],     # 7
    "glass": ["glass2.png"],           # 8
    "wood":["wood.png"],               # 9
    "leaves":["leaves3.png"],          # 10
}

item_names = []
for item in item_texture_names:
    item_names.append(item)
player_textures = []
sound_list = {"stone": "stone", "sand": "sand", "cobblestone": "stone", "bedrock": "stone", "grass": "grass", "dirt": "dirt", "plank": "stone", "glass":"stone", "wood":"stone", "leaves":"dirt", "short_grass":"grass", "flower":"grass"}
sound_files = {
    "stone": ["stone1.wav", "stone2.wav", "stone3.wav", "stone4.wav", "stone5.wav"],
    "sand": ["sand1.wav", "sand2.wav", "sand3.wav"],
    "grass": ["grass1.wav", "grass2.wav", "grass3.wav"],
    "dirt": ["dirt1.wav", "dirt2.wav"]
}
player_textures_files = {
    "body":"body/steve.png",
    "leg_r":"leg/steve.png",
    "hand1":"arm/steve.png",
    "hand2":"arm/steve.png",
    "head_r":"head/steve_r.png",
    "head_l":"head/steve_l.png"
}
gui_files = {
    "selected": "inventory/selected.png",
    "hotbar": "inventory/hotbar.png",
    "inventory": "inventory/inventory.png",
    "crafting": "inventory/crafting.png",
    "furnace": "inventory/furnace.png",
    "chest": "inventory/chest.png",
    "button": "button.png",
    "button_hover": "button_hover.png",
    "main_manu_background": "background/mc_background.png"
}
health_bar_files = {
    "health0": "health0.png",
    "health1": "health1.png",
    "health2": "health2.png",
    "health3": "health3.png",
    "health4": "health4.png",
    "health5": "health5.png",
    "health6": "health6.png",
    "health7": "health7.png",
    "health8": "health8.png",
    "health9": "health9.png",
    "health10": "health10.png",
    "health11": "health11.png",
    "health12": "health12.png",
    "health13": "health13.png",
    "health14": "health14.png",
    "health15": "health15.png",
    "health16": "health16.png",
    "health17": "health17.png",
    "health18": "health18.png",
    "health19": "health19.png",
    "health20": "health20.png"
}
structures = {}
gui_textures = {}

not_full_blocks = [True, False, False, False, False, False, False, False, False, True, True, True, True]
list_breaking_time = [-1, 5, 10, 10, -1, 3, 3]

# Generate texture IDs
block_texture_id = {name: i for i, name in enumerate(block_names)}

# Constants
item_size = 0
default_void_colour = "#ccd8ff"  # rgba(204,216,255,255)
texture_folder = "./assets/textures/blocks/"
sound_folder = "./assets/sounds/blocks/"
music_folder = "./assets/music/"
cursor_folder = "./assets/textures/cursor/"
gui_folder = "./assets/textures/GUI/"
player_folder = "./assets/textures/player/"
health_bar_folder = "./assets/textures/GUI/bars/Health/"
player_textures = {}

#--------TEXTURE LOADING-----------
def load_gui_textures():
    try:
        for key, file_path in gui_files.items():
            gui_textures[key] = pygame.image.load(gui_folder + file_path).convert_alpha()
        print(f"Loaded {len(gui_textures)} GUI textures.")
        return gui_textures
    except Exception as e:
        print("\nError loading GUI textures:\n", e)
        exit()

def load_cursor_textures(block_size, block_size_add):
    try:
        cursor = [pygame.transform.scale(pygame.image.load(cursor_folder + "cursor.png"), (block_size+block_size_add, block_size+block_size_add))]
        for i in range(1, 11):
            cursor.append(pygame.transform.scale(pygame.image.load(f"{cursor_folder}cursor{i}.png"), (block_size+block_size_add, block_size+block_size_add)))
        print(f"Loaded {len(cursor)} cursor textures.")
        return cursor
    except Exception as e:
        print("\nError loading cursor textures:\n", e)
        exit()

def load_block_textures(block_size, block_size_add):
    try:
        textures = []
        for i in block_texture_files:
            for j in range(len(block_texture_files[i])):
                textures.append(pygame.transform.scale(pygame.image.load(texture_folder + block_texture_files[i][j]), (block_size+block_size_add, block_size+block_size_add)))
        print(f"Loaded block textures.")
        return textures
    except Exception as e:
        print("\nError loading block textures:\n", e)
        exit()

def load_item_textures(item_size):
    try:
        item_textures = []
        for i in block_texture_files:
            for j in range(len(block_texture_files[i])):
                item_textures.append(pygame.transform.scale(pygame.image.load(texture_folder + block_texture_files[i][j]), (item_size, item_size)))
        print(f"Loaded item textures.")
        return item_textures
    except Exception as e:
        print("\nError loading item textures:\n", e)
        exit()

def load_player_textures(player_textures_files = player_textures_files):
    for key in player_textures_files.keys():
        player_textures[key] = pygame.image.load(player_folder + player_textures_files[key]).convert_alpha()
    player_textures["leg_l"] = pygame.transform.flip(player_textures["leg_r"], True, False)
    return player_textures
    try:
        pass
    except Exception as e:
        print("\nError loading player textures:\n", e)
        exit()

def load_health_bar_textures():
    try:
        health_bar = {}
        for key, file_path in health_bar_files.items():
            health_bar[key] = pygame.transform.scale(pygame.image.load(os.path.join(health_bar_folder, file_path)).convert_alpha(), (300, 32))
        
        print(f"Loaded {len(health_bar)} health bar textures.")
        return health_bar
    except Exception as e:
        print("\nError loading health bar textures:\n", e)
        exit()

def load_sound_effects():
    try:
        block_sound = {}
        for i in sound_files:
            block_sound[i] = []
            for j in range(len(sound_files[i])):
                block_sound[i].append(pygame.mixer.Sound(sound_folder + sound_files[i][j]))
        return block_sound
    except Exception as e:
        print("\nError loading sound effects:\n", e)
        exit()

def load_textures_and_sounds(block_size, block_size_add):
    from os import chdir, path
    chdir(path.dirname(__file__))
    global item_size
    item_size = block_size/8*7
    
    gui_t = load_gui_textures()
    cursor = load_cursor_textures(block_size, block_size_add)
    textures = load_block_textures(block_size, block_size_add)
    item_textures = load_item_textures(item_size)
    player_t = load_player_textures()
    block_sound = load_sound_effects()
    health_bar = load_health_bar_textures()
    
    return [cursor, textures, block_sound, item_textures, player_t, gui_t, health_bar]

def random_sound(name, block_sound):
    try:
        sound_type = sound_list[name]
    except:
        return gameExceptions.ErrorGettingSound(name)
    return random.choice(block_sound[sound_type])