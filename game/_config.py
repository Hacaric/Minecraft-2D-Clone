class ConfigFiles:
    UI_CONFIG_FILE = "./ui.config"
class Constants:
    random_seed_range = (1,999999)
    chunk_width = 64
    chunk_height = 64
    TPS = 60
    class Screen:
        width = 800
        height = 600
        block_in_screenX = 12
        FPS = 60
        
        block_size = width/block_in_screenX
        block_in_screenY = round(height/block_size)
    class Player:
        speed = 6 # BLOCK_SIZE / TICK
        gravity = -1.6
        jump_speed = 18 + 5
        size = (0.85, 1.7)

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
Constants.Player.speed /= Constants.TPS
Constants.Player.gravity /= Constants.TPS
Constants.Player.jump_speed /= Constants.TPS