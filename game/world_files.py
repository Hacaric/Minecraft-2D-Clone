import json
def isfile(file):
    try:
        # Attempt to open the file
        with open(file, 'r') as f:
            return True
    except FileNotFoundError:
        return False
def setup_filename(path, filename):
    #print(path + filename + ".json")
    #print("is file? : ", isfile(path+filename))
    if isfile(path + filename + ".json"):
        filename += "#0"
        while isfile(path + filename + ".json"):
            filename = filename[:filename.index("#")+1]+str(int(filename[filename.index("#")+1:]) + 1)
    #print(path+filename)
    return filename

def save_data(dict, filename = "", path = "./saves/", overwrite = False, filetype = ".json"):
    if filename == "":
        filename = "new_world"
    if not overwrite:
        filename = setup_filename(path, filename) + filetype
    with open(path + filename, 'w') as f:
        json.dump(dict, f)
    return f"Saved succesfully written to {path + filename + filetype}"


def load_data(filename, path = "saves/"):
    with open(path + filename, 'r') as f:
        data_loaded = json.load(f)
    return data_loaded