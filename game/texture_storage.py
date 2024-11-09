import pygame
import random

# Texture and sound data
#block_names = ["air", "sand", "cobblestone", "stone", "bedrock", "grass", "dirt", "plank", "glass", "wood", "leaves", "short_grass"]
block_texture_files = {
    "air": ["#.png"],
    "sand": ["sand.png"],
    "cobblestone": ["Cobblestone.png"],
    "stone": ["rock.png"],
    "bedrock": ["bedrock.png"],
    "grass": ["grass.png"],
    "dirt": ["dirt.png"],
    "plank": ["woodenplanks.png"],
    "glass": ["glass2.png"],
    "wood":["wood.png"],
    "leaves":["leaves2.png"],
    "short_grass":["short_grass.png"],
    "flower":["rose3.png"]
}
block_names = []
for item in block_texture_files:
    block_names.append(item)
#item_names = ["air", "sand", "cobblestone", "stone", "bedrock", "grass", "dirt", "plank", "glass", "wood", "leaves"]
item_texture_names = {
    "air": ["#.png"],
    "sand": ["sand.png"],
    "cobblestone": ["Cobblestone.png"],
    "stone": ["rock.png"],
    "bedrock": ["bedrock.png"],
    "grass": ["grass.png"],
    "dirt": ["dirt.png"],
    "plank": ["woodenplanks.png"],
    "glass": ["glass2.png"],
    "wood":["wood.png"],
    "leaves":["leaves3.png"]
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
    "main_manu_background": "background/griffpatch.png"
}
structures = {}
gui_textures = {}

not_full = [True, False, False, False, False, False, False, False, False, True, True, True, True]
list_breaking_time = [-1, 5, 10, 10, -1, 3, 3]

# Generate texture IDs
block_texture_id = {name: i for i, name in enumerate(block_names)}

# Constants
item_size = 0
default_void_colour = "#ccd8ff"  # rgba(204,216,255,255)
texture_folder = "assets/textures/blocks/"
sound_folder = "assets/sounds/blocks/"
music_folder = "assets/music/"
cursor_folder = "assets/textures/cursor/"
gui_folder = "assets/textures/GUI/"
player_folder = "assets/textures/player/"
player_textures = {}

#--------TEXTURE LOADING-----------
def load_textures_and_sounds(block_size, block_size_add):
    global item_size
    item_size = block_size/8*7
    try:
        for key, file_path in gui_files.items():
            gui_textures[key] = pygame.image.load(gui_folder + file_path).convert_alpha()
        print(f"Loaded {len(gui_textures)} GUI textures.")
        cursor = [pygame.transform.scale(pygame.image.load(cursor_folder + "cursor.png"), (block_size+block_size_add, block_size+block_size_add))]
        for i in range(1, 11):
            cursor.append(pygame.transform.scale(pygame.image.load(f"{cursor_folder}cursor{i}.png"), (block_size+block_size_add, block_size+block_size_add)))
        print(f"Loaded {len(cursor)} cursor textures.")
        textures = []
        for i in block_texture_files:
            for j in range(len(block_texture_files[i])):
                textures.append(pygame.transform.scale(pygame.image.load(texture_folder + block_texture_files[i][j]), (block_size+block_size_add, block_size+block_size_add)))
        print(f"Loaded block textures.")
        item_textures = []
        for i in block_texture_files:
            for j in range(len(block_texture_files[i])):
                item_textures.append(pygame.transform.scale(pygame.image.load(texture_folder + block_texture_files[i][j]), (item_size, item_size)))
        print(f"Loaded item textures.")
        for key in player_textures_files.keys():
            player_textures[key] = pygame.image.load(player_folder + player_textures_files[key]).convert_alpha()
        player_textures["leg_l"] = pygame.transform.flip(player_textures["leg_r"], True, False)
    except Exception as e:
        print("\nError loading textures:\n", e)
        exit()
    #-----------TEXTURE LOADING END------------

    # Load sound effects
    block_sound = {}
    for i in sound_files:
        block_sound[i] = []    #pygame.mixer.Sound("assets/sounds/grass.wav").play()
        for j in range(len(sound_files[i])):
            block_sound[i].append(pygame.mixer.Sound(sound_folder + sound_files[i][j]))
    return [cursor, textures, block_sound, item_textures]

def random_sound(name, block_sound):
    sound_type = sound_list[name]
    return random.choice(block_sound[sound_type])