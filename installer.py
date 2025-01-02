import os
import shutil
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y

# Define the source folder containing the game files
GAME_FOLDER_NAME = "Minecraft_2D"

def log_message(message):
    """Log a message to the installation window."""
    log_window.insert("end", message + "\n")
    log_window.see("end")
    root.update_idletasks()


def choose_installation_directory():
    """Let the user select an installation directory."""
    folder = filedialog.askdirectory(title="Select Installation Directory")
    if folder:
        install_game(folder)

def install_game(game_folder):
    import requests
    from zipfile import ZipFile
    import os
    import shutil

    if os.path.exists(f"{game_folder}/{GAME_FOLDER_NAME}/"):
        check1 = messagebox.askyesno("Warning", f"Game already installed!\nYou can run game by running file {os.path.join(game_folder, GAME_FOLDER_NAME, 'launcher/launcher.py')}\nDo you want to continue?")
        if not check1:
            exit(1)
        check2 = messagebox.askyesno("Warning", f"Are you sure? All files will be deleted.")
        if not check2:
            exit(1)
        shutil.rmtree(f"{game_folder}/{GAME_FOLDER_NAME}/")
    os.makedirs(f"{game_folder}/{GAME_FOLDER_NAME}/.update/update_files/")
    update_zip_path = f'{game_folder}/{GAME_FOLDER_NAME}/.update/version.zip'
    extract_path = f'{game_folder}/{GAME_FOLDER_NAME}/.update/update_files/'
    extract_only_this_folder_from_zip = "./"
    old_files_path = f'{game_folder}/{GAME_FOLDER_NAME}/'

    # GitHub repository URL
    repository_name = 'Minecraft-2D-Clone'
    addr = f"https://github.com/Hacaric/{repository_name}/archive/refs/heads/main.zip"
    url = addr

    # Ensure directories exist
    os.makedirs(os.path.dirname(update_zip_path), exist_ok=True)
    os.makedirs(extract_path, exist_ok=True)
    os.makedirs(old_files_path, exist_ok=True)

    # Download the file
    log_message("Downloading update from github...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(update_zip_path, 'wb') as file:
            file.write(response.content)
        log_message('File downloaded successfully')
    else:
        log_message('Failed to download file')
        exit(1)

    # Unzip the file
    log_message("Trying to unzip...")
    try:
        with ZipFile(update_zip_path, 'r') as zObject:
            zObject.extractall(path=extract_path)
        log_message('Files unzipped successfully')
    except Exception as e:
        log_message(f'Failed to unzip files: {e}')
        exit(1)

    #Rename to repository name

    try:
        old_folder = extract_path + repository_name + "-main"
        new_folder = extract_path + repository_name
        if os.path.exists(new_folder):
            shutil.rmtree(new_folder) 
        os.rename(old_folder, new_folder)
    except Exception as e:
        log_message(f"Failed renaming directory {extract_path}{old_folder} to {repository_name} error: {e}")
        exit(1)

    # Delete the zip file
    log_message("Deleting zip...")
    os.remove(update_zip_path)

    log_message("\nCopying files...")
    new_files = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
    for filename in new_files:
        log_message(f"|---Updating file {filename}")
        os.replace(
            os.path.join(extract_path, repository_name, extract_only_this_folder_from_zip, filename),
            os.path.join(old_files_path, filename)
            )
        #os.replace(f"{extract_path}{repository_name}/{filename}", old_files_path+filename)

    log_message("\nCopying folders...")
    new_folders = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if not os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
    for folder_name in new_folders:
        if os.path.exists(os.path.join(old_files_path, folder_name)):
            log_message(f"|---Updating folder {os.path.join(old_files_path, folder_name)}")
            shutil.rmtree(os.path.join(old_files_path, folder_name))
        os.makedirs(os.path.join(old_files_path,folder_name))
        os.rename(
            os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,folder_name), 
            os.path.join(old_files_path,folder_name)

        )

    log_message("\nInstallation completed.")
    log_message("Cleaning up...")
    try: 
        try:
            shutil.rmtree(extract_path)
        except:
            pass
        os.makedirs(extract_path)
    except Exception as e:
        log_message(f"Failed cleaning, repository probably contained directory. Error: {e}")
        exit(1)
    log_message("\nUpdated successfully.")
    if messagebox.askyesno("Installation info.", "Installed sucessfully.\nRun launcher?"):
        import subprocess
        subprocess.Popen("python", f"./{GAME_FOLDER_NAME}/launcher/launcher.py")
    exit(1)#TODO



# Create the installer GUI
def create_installer():
    global root, log_window
    root = Tk()
    root.title("Game Installer")
    root.geometry("600x400")

    # Add a label
    label = Label(root, text="Welcome to the Game Installer!", font=("Arial", 14))
    label.pack(pady=20)

    # Add a button to choose the installation directory
    install_button = Button(root, text="Install Game", command=choose_installation_directory, font=("Arial", 12))
    install_button.pack(pady=10)

    log_frame = Scrollbar(root, orient=VERTICAL)
    log_frame.pack(side=RIGHT, fill=Y)


    log_window = Text(root, wrap="word", yscrollcommand=log_frame.set, height=15, width=70)
    log_window.pack(pady=10)
    log_frame.config(command=log_window.yview)


    # Add an exit button
    exit_button = Button(root, text="Exit", command=root.quit, font=("Arial", 12))
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_installer()
