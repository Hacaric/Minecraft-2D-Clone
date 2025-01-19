import os
import json

def rename_sprites(directory):
    # Locate the sprite.json file in the specified directory
    json_file = os.path.join(directory, 'sprite.json')
    
    if not os.path.isfile(json_file):
        print("sprite.json file not found in the specified directory.")
        return

    # Load the sprite.json file
    with open(json_file, 'r') as f:
        project_data = json.load(f)

    # Extract costumes from the JSON data
    costumes = project_data.get('costumes', [])

    print(f"Found {len(costumes)} costumes in the JSON file.")

    # Loop through the costumes in the JSON file
    for costume in costumes:
        asset_id = costume.get('assetId', '')
        original_name = costume.get('name', '')
        md5ext = costume.get('md5ext', '')
        if not asset_id or not original_name or not md5ext:
            print(f"Skipping incomplete costume data: {costume}")
            continue

        extension = md5ext.split('.')[-1]

        # Create the expected current filename
        current_filename = f"{asset_id}.{extension}"
        current_filepath = os.path.join(directory, current_filename)

        # Check if the file exists in the directory
        if os.path.exists(current_filepath):
            new_filename = f"{original_name}.{extension}"
            new_filepath = os.path.join(directory, new_filename)

            # Rename the file
            os.rename(current_filepath, new_filepath)
            print(f"Renamed: {current_filename} -> {new_filename}")
        else:
            print(f"File {current_filename} not found in directory.")

if __name__ == "__main__":
    # Specify the directory containing the sprites and the sprite.json file
    directory = input("Enter the directory containing the sprites and sprite.json: ")

    if os.path.isdir(directory):
        rename_sprites(directory)
    else:
        print("Invalid directory path!")


