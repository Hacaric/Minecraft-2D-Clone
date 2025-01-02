def make_update():
    import requests
    from zipfile import ZipFile
    import os
    import shutil

    def folder_in_directory_tree(target_dir, folder_name):
        for item in [os.path.join(target_dir, folder) for folder in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, folder))]:
            if folder_name == os.path.basename(item):
                return item
            addr = folder_in_directory_tree(item, folder_name)
            if addr:
                return addr
        return False


    NOT_DELETE_DIR = ["saves", "launcher"]

    # GitHub repository URL
    repository_name = 'Minecraft-2D-Clone'
    addr = f"https://github.com/Hacaric/{repository_name}/archive/refs/heads/main.zip"
    url = addr

    # Paths
    update_zip_path = '../.update/version.zip'
    extract_path = '../.update/update_files/'
    extract_only_this_folder_from_zip = "../"
    old_files_path = '../'

    # Ensure directories exist
    os.makedirs(os.path.dirname(update_zip_path), exist_ok=True)
    os.makedirs(extract_path, exist_ok=True)
    os.makedirs(old_files_path, exist_ok=True)

    # Download the file
    print("Downloading update from github...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(update_zip_path, 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully')
    else:
        print('Failed to download file')
        exit(1)

    # Unzip the file
    print("Trying to unzip...")
    try:
        with ZipFile(update_zip_path, 'r') as zObject:
            zObject.extractall(path=extract_path)
        print('Files unzipped successfully')
    except Exception as e:
        print(f'Failed to unzip files: {e}')
        exit(1)

    #Rename to repository name

    try:
        old_folder = extract_path + repository_name + "-main"
        new_folder = extract_path + repository_name
        if os.path.exists(new_folder):
            shutil.rmtree(new_folder) 
        os.rename(old_folder, new_folder)
    except Exception as e:
        print(f"Failed renaming directory {extract_path}{old_folder} to {repository_name} error: {e}")
        exit(1)
    # Delete the zip file
    print("Deleting zip...")
    os.remove(update_zip_path)
    print("\nReplacing files...")
    new_files = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
    for filename in new_files:
        print(f"|---Updating file {filename}")
        os.replace(
            os.path.join(extract_path, repository_name, extract_only_this_folder_from_zip, filename),
            os.path.join(old_files_path, filename)
            )
        #os.replace(f"{extract_path}{repository_name}/{filename}", old_files_path+filename)

    for file_name in NOT_DELETE_DIR:
        not_delete = folder_in_directory_tree(os.path.join(old_files_path), file_name)
        if not_delete and os.path.exists(not_delete):
            print(f"|---Not updating folder (deleting from downloaded files): {not_delete}.")
            file_to_delete = folder_in_directory_tree(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip), file_name)
            if file_to_delete:
                shutil.rmtree(file_to_delete)
            else:
                print(f"\nError looking for existing file {file_to_delete}\n")

    print("\nUpdating folders...")
    new_folders = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if not os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
    for folder_name in new_folders:
        if os.path.exists(os.path.join(old_files_path, folder_name)):
            print(f"|---Updating folder {os.path.join(old_files_path, folder_name)}")
            shutil.rmtree(os.path.join(old_files_path, folder_name))
        os.makedirs(os.path.join(old_files_path,folder_name))
        os.rename(
            os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,folder_name), 
            os.path.join(old_files_path,folder_name)

        )

    print("\nReplacing completed.")
    print("Cleaning up...")
    try: 
        try:
            shutil.rmtree(extract_path)
        except:
            pass
        os.makedirs(extract_path)
    except Exception as e:
        print(f"Failed cleaning, repository probably contained directory. Error: {e}")
        exit(1)
    print("\nUpdated successfully.")