import json
import random
import os
from typing import Literal
import zlib
import _config
import sys
import re as regex
from world_serverside import World
import ast
import typing
import tkinter
import tkinter.filedialog
from gameLogger import log

__script_name__ = os.path.basename(__file__)

# def isfile(file):
    # return os.path.isfile(file)
    # try:
    #     # Attempt to open the file
    #     with open(file, 'r') as f:
    #         return True
    # except FileNotFoundError:
    #     return False
    
def setup_filename(path, filename:str, overwrite = False) -> str:
    # log("is file? : ", os.path.join(path, filename + _config.Constants.WorldFile.extension))
    # log("yes :D" if os.path.isfile(os.path.join(path, filename + _config.Constants.WorldFile.extension)) else "no D:")
    if path == "/":
        raise Exception(f"WHAT HAVE YOU DONE? DONT SAVE YOUR WORLD FILE IN '/'! ({__script_name__} in setup_filename())")


    if filename[:-len(_config.Constants.WorldFile.extension)] == _config.Constants.WorldFile.extension:
        filename = filename[:-len(_config.Constants.WorldFile.extension)]

    if (not overwrite) and os.path.isfile(os.path.join(path, filename + _config.Constants.WorldFile.extension)):
        
        # Creates unique filename by adding #num and counting up num to find unused name.

        num = 1
        filename = filename+"#"+str(num)
        while os.path.isfile(os.path.join(path, filename + _config.Constants.WorldFile.extension)):
            filename = filename[:-len(str(num-1)) - 1]+"#"+str(num)
            #                                   x - 1 to delete the '#'
            num += 1
    filename += _config.Constants.WorldFile.extension
        
    #log(path+filename)
    if not os.path.isdir(path):
        os.makedirs(path)
    return os.path.join(path, filename)

# def save_data(dict, filename = "", path = "./saves/", overwrite = False, filetype = _config.Constants.WorldFile.extension):
#     if filename == "":
#         filename = "new_world"
#     if not overwrite:
#         filename = setup_filename(path, filename) + filetype
#     with open(path + filename, 'w') as f:
#         json.dump(dict, f)
#     return f"Saved succesfully written to {path + filename + filetype}"


# def load_data(filename, path = "saves/"):
#     with open(path + filename, 'r') as f:
#         data_loaded = json.load(f)
#     return data_loaded

def prompt_file(initial_dir = None) -> str:
    """Create a Tk file dialog and cleanup when finished"""
    if initial_dir is None:
        initial_dir = os.path.dirname(__file__)
    # initial_dir = os.path.dirname(initial_dir)
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top, initialdir=initial_dir)
    top.destroy()
    return file_name

# def new_world(path, name, gamemode, seed):
#     filename = setup_filename(path, name)
#     log("[New world] Filename:", filename)
#     log("[New world] Gamemode:", gamemode)
#     if type(seed) == int:
#         pass
#     elif seed == "":
#         seed = random.randint(0,999999)
#     else:
#         seed = hash(seed)
#     log("[New world] Seed:", seed)
class WorldFile:
    def __init__(self, object:typing.Any|World, path:str, filename_without_extention:str, save_on_init=True, overwrite = False):
        """
        Requerements:
        - 'object' variable should have method object.parse()->dict or you wont be able save your file
        - Every key and value in object.parse()->dict must have __str__ method defined.
        """
        filename = filename_without_extention
        self.overwrite = overwrite
        self.world = object
        self.filepos = setup_filename(path, filename, overwrite = self.overwrite)
        if save_on_init:
            self.save()

    def save(self, encoding_mode:Literal["readable","raw"] = "readable"):
        log("Saving world...", color="#b800ae")
        try:
            world_data:dict[typing.Any, typing.Any] = self.world.parse()
        except Exception as e:
            log(f"Error calling {self.world}.parse(): {e}")
            raise e # xd
        encoding_mode = str(encoding_mode) # For case it does some shananogans with Literal type :D, just to make it work
        if not (encoding_mode in _config.Constants.WorldFile.save_modes):
            encoding_mode = _config.Defaults.WorldFile.default_save_mode
        match encoding_mode:
            case "raw":
                json_data:str = json.dumps(world_data)
                raw_data:bytes = zlib.compress(json_data.encode(_config.Constants.WorldFile.str_encoding))
                with open(self.filepos, "wt") as f:
                    f.write(f"format:{encoding_mode}\n")
                with open(self.filepos, "ab") as f:
                    f.write(raw_data)
            case "readable":
                compressed_data = {}
                for key, value in world_data.items():
                    value = str(value)
                    if sys.getsizeof(value) >= _config.Constants.WorldFile.readable_mode_min_bytes_for_compression:
                        value = str(zlib.compress(value.encode(_config.Constants.WorldFile.str_encoding)))
                        keyname = "E" + key # E as Encoded
                    else:
                        keyname = "R" + key # R as Raw
                    compressed_data[keyname] = value
                raw_data = json.dumps(compressed_data)#, separators=("\n", "="))

                with open(self.filepos, "wt") as f:
                    f.write(f"format:{encoding_mode}\n")
                with open(self.filepos, "at") as f:
                    f.write(raw_data)
    @classmethod
    def loadFileDataIntoDict(self, filedata:str) -> dict:
        # log("Checkpoint A.1")
        header_end = filedata.index("\n")
        header = filedata[:header_end]
        encoding_mode = header.split(":")[1]
        filedata = filedata[header_end+1:]
        # log("Checkpoint A.2", header, "\nData:", filedata, ";")
        match encoding_mode:
            case "raw":
                # log("Checkpoint A.A.1")
                json_data:bytes = zlib.decompress(filedata)
                world_data = json.loads(json_data)
                # log("Checkpoint A.A.2")
                return world_data
                
            case "readable":
                #filedata = filedata.replace("\n", ",").replace("=", ":")
                # log("Checkpoint A.B.1", filedata)
                json_data = json.loads(filedata)
                decompressed_data = {}
                # log("Checkpoint A.B.2")
                for key, value in json_data.items():
                    value = str(value)
                    if key[0] == "E":
                        value = zlib.decompress(ast.literal_eval(value)).decode(_config.Constants.WorldFile.str_encoding)
                        key = key[1:]
                    elif key[0] == "R":
                        key = key[1:]
                        pass
                    else:
                        log(f"Invalid world data: {key} = {value}: missing key prefix E-encoded/R-raw.\nPicking default options: raw")
                        key = key[1:]
                        pass
                    decompressed_data[key] = value
                # log("Checkpoint A.B.3", decompressed_data)
                return decompressed_data


def test():
    try:
        # class TestWorld:
        #     def __init__(self, data:dict):
        #         self.data = data
        #     def parse(self):
        #         return self.data
        # log("Checkpoint1")
        # w = World(16,16)
        # log("Checkpoint2")
        # w.generateChunk(2)
        # log("Checkpoint3")
        # wfile = WorldFile(w, os.path.join(os.path.dirname(__file__), "world_saves"), "test_world_1", save_on_init=False)
        # log("Checkpoint4", "Filepos: ", wfile.filepos)
        # w.chunks[2].setBlock(0,0,3)
        # log("Checkpoint5")
        # wfile.save()
        # log("Checkpoint6")
        w2 = World(16,16)
        # w.chunks[0] = Empty
        log("Checkpoint7")
        with open("/home/hacaric/programming/Minecraft_Paper/world_saves/new_world.txt", "rt") as f:
            file_data = "".join(f.readlines())

        log("Checkpoint8")
        world_data = WorldFile.loadFileDataIntoDict(file_data)
        w2.loadFromDict(world_data, overwrite_loaded_chunks=True)
        log("Checkpoint9", w2.chunks.items())
        # log("\nTest of no-information-loss:", "passed" if w2.chunks[2].blocks == w.chunks[2].blocks else "failed")
        log(f"\nTest of {__script_name__} passed without error!\n:)")
    except Exception as e:
        log(f"\nTest of {__script_name__} failed: {e}\n:(")

if __name__ == "__main__":
    log(f"Starting test of {__script_name__}...")
    test()