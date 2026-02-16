import os
def fullPath(file):
    return os.path.join(os.path.dirname(__file__), file)
class ConfigFiles:
    # UI_CONFIG_FILE = "./ui.config"
    BIOME_CONFIG_FILE = fullPath("./biomes.json")
class Constants:
    random_seed_range = (1,999999)
    chunk_width = 64
    chunk_height = 64
    TPS = 60
    gamemode_enum = {"survival":0, "creative":1, "s":0, "c":1}
    class Player:
        speed = 6 # BLOCK_SIZE / TICK
        gravity = -1.6
        jump_speed = 18 + 5
        size = (0.85, 1.7)

    class Inventory:
        # vvv Changing this may cause errors while displaying inventory. Don't change this until implemented 
        width = 9
        height = 4
        # ^^^

        max_stack_size = 64

    class World:
        GenChecksPerSec = 1 # Tries to generate new chunks (if needed) some number of times per seconds
        MaxGenerationThreads = 5
        MaxBlockIndex = 65534 # Bigger values will mess up world files (especially when block are stored as chr(block_index))

    class WorldFile:
        save_modes = ["readable", "raw"]
        # Readable: only large values like world data are enrypted, its easy to edit json data
        # Raw: all data are put in json format and thrown into zlib compressor. It will not be readable
        readable_mode_min_bytes_for_compression = 128 # 128 beacause a string "a" is 42 bytes ._. why python?? chatgpt said its bunch of metadata, and its pretty much constant so it should be fine now
        str_encoding = "utf-8"
        extension = ".txt"

class Defaults:
    class WorldFile:
        default_save_mode = "readable"
        default_saves_dir = "./world_saves"
        default_world_name = "new_world"
    class Screen:
        width = 800
        height = 600
        block_in_screenX = 12
        FPS = 60
        ReducedFPS = 10 # When window is not focused
        UseReducedFPS = True
        
        block_size = int(width/block_in_screenX)
        block_in_screenY = round(height/block_size)
        def get_block_size_properties(window_width, window_height):
            block_size = int(window_width/Defaults.Screen.block_in_screenX)
            block_in_screenY = round(window_height/block_size)
            return block_size, block_in_screenY
    class PlayerRender:
        size_dict = {}
        size_dict["body"] = (0.8, 1.8)
        size_dict["leg_r"] = (0.4, 1.0)
        size_dict["leg_l"] = (0.4, 1.0)
        size_dict["head_r"] = (0.5, 0.5)
        size_dict["head_l"] = (0.5, 0.5)

Constants.Player.speed /= Constants.TPS
Constants.Player.gravity /= Constants.TPS
Constants.Player.jump_speed /= Constants.TPS