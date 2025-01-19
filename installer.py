# 
# To execute this file, double-click it or run the command: $ python installer.py
#
# If your Python installation cannot be executed this way, verify if Python is 
# installed correctly. Alternatively, update the variable below to match the command 
# used to run Python in your console (e.g., "python3" or a custom alias).
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
python_shell_command = "python"
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

import os
import shutil
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y, INSERT, DISABLED, NORMAL
import subprocess

# Define the source folder containing the game files
GAME_FOLDER_NAME = "Minecraft_2D"
GAME_IDENTIFIER = ".identifierMinecraft2D"

def folder_in_directory_tree(target_dir, folder_name, depth=0):
    try:
        if depth >= 7:
            return False
        for item in [os.path.join(target_dir, folder) for folder in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, folder))]:
            if folder_name == os.path.basename(item):
                return item
            addr = folder_in_directory_tree(item, folder_name, depth=depth+1)
            if addr:
                return addr
        return False
    except:
        return False

def is_directory_in_parents(target_directory, directory_name):
    current_path = os.path.abspath(target_directory)
    
    while True:
        parent_path, current_dir = os.path.split(current_path)
        if current_dir == directory_name:
            return os.path.join(current_path)
        if not parent_path or parent_path == current_path:
            # Reached the root directory
            break
        current_path = parent_path
    
    return False

def log_message(message):
    """Log a message to the installation window."""
    log_window.config(state=NORMAL)
    log_window.insert("end", message + "\n")
    log_window.see("end")
    root.update_idletasks()
    log_window.config(state=DISABLED)


def choose_installation_directory(title="Select Installation Directory"):
    """Let the user select an installation directory."""
    folder = filedialog.askdirectory(title=title)

    if folder:
        return folder
    else:
        print("error choosing file (line 39)")

def run_launcher():
    starting_game_folder = choose_installation_directory(title="Select Game Directory")
    log_message("Looking for directory...")
    if os.path.basename(starting_game_folder) == GAME_IDENTIFIER:
        game_folder = starting_game_folder
    else:
        log_message(f"Looking for game directory in parents of '{starting_game_folder}'.")
        game_folder = is_directory_in_parents(starting_game_folder, GAME_IDENTIFIER)
        if game_folder == False:
            log_message(f"Looking for game directory in tree of '{starting_game_folder}'.")
            game_folder = folder_in_directory_tree(starting_game_folder, GAME_IDENTIFIER)
            if game_folder == False:
                messagebox.showerror("Not found", "Game wasn't found in current directory.\nTry installing it.")
                return
    option = messagebox.askquestion("Game found!", "Launcher found!\nRun launcher and close installer?")
    if option == "yes":
        subprocess.Popen([python_shell_command, f"{game_folder}/../launcher/launcher.py"], shell=False)
        exit(1)

def install_game(game_folder):
    import requests
    from zipfile import ZipFile
    import os
    import shutil

    if messagebox.askyesno("Create folder?", f"Create folder named {GAME_FOLDER_NAME}? (if not, app will be installed directly into chosen directory.)"):
        
        os.makedirs(f"{game_folder}/{GAME_FOLDER_NAME}/.update/update_files/")
        update_zip_path = f'{game_folder}/{GAME_FOLDER_NAME}/.update/version.zip'
        extract_path = f'{game_folder}/{GAME_FOLDER_NAME}/.update/update_files/'
        extract_only_this_folder_from_zip = "./"
        old_files_path = f'{game_folder}/{GAME_FOLDER_NAME}/'
        if os.path.exists(f"{game_folder}/{GAME_FOLDER_NAME}/"):
            check1 = messagebox.askyesno("Warning", f"Game already installed!\nYou can run game by running file {os.path.join(game_folder, GAME_FOLDER_NAME, 'launcher/launcher.py')}\nDo you want to continue installation?")
            if not check1:
                return
            check2 = messagebox.askyesno("Warning", f"Are you sure? All files will be deleted.")
            if not check2:
                return
            shutil.rmtree(f"{game_folder}/{GAME_FOLDER_NAME}/")
    else:
        os.makedirs(f"{game_folder}/.update/update_files/")
        update_zip_path = f'{game_folder}/.update/version.zip'
        extract_path = f'{game_folder}/.update/update_files/'
        extract_only_this_folder_from_zip = "./"
        old_files_path = f'{game_folder}/'

        if os.path.exists(f"{game_folder}/{GAME_IDENTIFIER}/"):
            check1 = messagebox.askyesno("Warning", f"Game already installed!\nYou can run game by running file {os.path.join(game_folder, 'launcher/launcher.py')}\nDo you want to continue installation?")
            if not check1:
                return
            check2 = messagebox.askyesno("Warning", f"Are you sure? This will likely produce an error. \nTry deleting all game files first(include {GAME_IDENTIFIER} folder).")
            if not check2:
                return
    log_message(f"Installing into directory: {game_folder}")


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
    try:
        new_files.remove(os.path.basename(__file__))
    except:
        print("Error removing installer.py from installation.")
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
    # if messagebox.askyesno("Send statistic data?", "Send statistic data?\n- OS"):
    #     subject = "Test Email"
    #     body = "This is a test email sent using sendmail."
    #     sender_email = "your-email@example.com"
    #     recipient_email = "recipient@example.com"
    #     email_message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {recipient_email}\n\n{body}"
    #     with os.popen("/usr/sbin/sendmail -t", "w") as sendmail:
    #         sendmail.write(email_message)
    if messagebox.askyesno("Installation info.", "Installed successfully.\nRun launcher?"):
        run_launcher()
        exit(1)#TODO



# Create the installer GUI
def create_installer():
    global root, log_window
    root = Tk()
    root.title("Minecraft 2D Installer")
    root.geometry("600x400")

    # Add a label
    label = Label(root, text="Welcome to Minecraft 2D Installer!", font=("Arial", 14))
    label.pack(pady=20)

    # Add a button to choose the installation directory
    install_button = Button(root, text="Install Game", command=lambda:install_game(choose_installation_directory()), font=("Arial", 12))
    install_button.pack(pady=10)

    install_button = Button(root, text="Run game", command=run_launcher, font=("Arial", 12))
    install_button.pack(pady=10)

    log_frame = Scrollbar(root, orient=VERTICAL)
    log_frame.pack(side=RIGHT, fill=Y)


    log_window = Text(root, wrap="word", yscrollcommand=log_frame.set, height=15, width=70)
    log_window.pack(pady=10)
    from datetime import datetime
    log_window.insert(INSERT, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nLog:\n")
    log_frame.config(command=log_window.yview)
    log_window.config(state=DISABLED)


    # Add an exit button
    exit_button = Button(root, text="Exit", command=root.quit, font=("Arial", 12))
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_installer()
