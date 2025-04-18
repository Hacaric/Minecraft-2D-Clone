# 
# To execute this file, double-click it or run the command: $ python installer.py
#
# If your Python installation cannot be executed this way, verify if Python is 
# installed correctly. Alternatively, update the variable below to match the command 
# used to run Python in your console (e.g., "python3" or a custom alias).
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
python_shell_command = "python"
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

depedencies_missing = []
try:
    import os
except ImportError:
    depedencies_missing.append("os")

try:
    import shutil
except ImportError:
    depedencies_missing.append("shutil")

try:
    import subprocess
except ImportError:
    depedencies_missing.append("subprocess")

try:
    from tkinter import (
        Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y, INSERT, DISABLED, NORMAL
    )
except ImportError:
    depedencies_missing.append("tkinter")

try:
    import requests
except ImportError:
    depedencies_missing.append("requests")

try:
    from zipfile import ZipFile
except ImportError:
    depedencies_missing.append("zipfile")

try:
    from datetime import datetime
except ImportError:
    depedencies_missing.append("datetime")

if depedencies_missing:
    print("Missing dependencies:")
    for dep in depedencies_missing:
        print(f"- {dep}")
    print("Do you want us to install them for you? (using pip)")
    option = input("y/n: ")
    if option == "y":
        for dep in depedencies_missing:
            if dep == "os":
                print("os is a built-in module and cannot be installed.")
            elif dep == "shutil":
                print("shutil is a built-in module and cannot be installed.")
            elif dep == "tkinter":
                print("tkinter is a built-in module and cannot be installed.")
            elif dep == "subprocess":
                print("subprocess is a built-in module and cannot be installed.")
            elif dep == "requests":
                print("Installing requests...")
                subprocess.check_call([python_shell_command, "-m", "pip", "install", "requests"])
                import requests
                print("requests installed successfully.")
            elif dep == "zipfile":
                print("zipfile is a built-in module and cannot be installed.")
            elif dep == "datetime":
                print("datetime is a built-in module and cannot be installed.")
            elif dep == "pip":
                print("pip is a built-in module and cannot be installed.")
    else:
        print("Please install the missing dependencies manually.")
        exit(1)

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
        return None

def run_launcher():
    starting_game_folder = choose_installation_directory(title="Select Game Directory")
    if starting_game_folder is None:
        return
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
    if game_folder is None:
        return
    if messagebox.askyesno("Create folder?", f"Create folder named {GAME_FOLDER_NAME}? (if not, app will be installed directly into chosen directory.)"):
        try:
            os.makedirs(f"{game_folder}/{GAME_FOLDER_NAME}/.update/update_files/")
        except Exception as e:
            log_message(f"Failed creating directory {game_folder}/{GAME_FOLDER_NAME}/.update/update_files/ error: {e}")
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
        return "error"

    # Unzip the file
    log_message("Trying to unzip...")
    try:
        with ZipFile(update_zip_path, 'r') as zObject:
            zObject.extractall(path=extract_path)
        log_message('Files unzipped successfully')
    except Exception as e:
        log_message(f'Failed to unzip files: {e}')
        return "error"

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
    try:
        for filename in new_files:
            log_message(f"|---Updating file {filename}")
            os.replace(
                os.path.join(extract_path, repository_name, extract_only_this_folder_from_zip, filename),
                os.path.join(old_files_path, filename)
                )
            #os.replace(f"{extract_path}{repository_name}/{filename}", old_files_path+filename)
    except Exception as e:
        log_message(f"Failed copying files: {e}. Aborting...")
        return "error"

    log_message("\nCopying folders...")
    try:
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
    except Exception as e:
        log_message(f"Failed copying folders: {e}. Aborting...")
        return "error"

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
        return "error"
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
def start_install_game(game_folder):
    """Start the installation process."""
    log_message("Starting installation...")
    if install_game(game_folder) == "error":
        messagebox.showerror("Error", "Installation failed. You can report this error on GitHub.")
        log_message("Installation failed. Please report on https://github.com/Hacaric/Minecraft-2D-Clone/issues. Include all logs.")
        return
    else:
        messagebox.showinfo("Success", "Installation completed successfully.")
        return

def copy_to_clipboard(text):
    """Copy text to the clipboard."""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Keep the clipboard updated
    except Exception as e:
        log_message(f"Failed to copy to clipboard: {e}")
def report_issues():
    copy_to_clipboard(log_window.get("1.0", "end-1c"))
    if messagebox.askokcancel("Report issues", "Log copied to clipboard.\nDo you want to open browser to report issues?"):
        try:
            import webbrowser
        except ImportError:
            if messagebox.askyesno("Error", "Webbrowser module not found. Install it?"):
                subprocess.check_call([python_shell_command, "-m", "pip", "install", "webbrowser"])
                import webbrowser
            else:
                return
        # Open the URL in the default web browser
        webbrowser.open(f"https://github.com/Hacaric/Minecraft-2D-Clone/issues/new?title=Automatic Issue Report&body=Log time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nLogs:\n{log_window.get("1.0", "end-1c").replace("\n", "\n- ")}".replace(" ", "%20").replace("\n", "%0A"), new=2)


# Create the installer GUI
def create_installer():
    global root, log_window
    root = Tk()
    root.title("Minecraft 2D Installer")
    root.geometry("800x600")

    # Add a label
    label = Label(root, text="Welcome to Minecraft 2D Installer!", font=("Arial", 14))
    label.pack(pady=20)

    # Add a button to choose the installation directory
    install_button = Button(root, text="Install Game", command=lambda:start_install_game(choose_installation_directory()), font=("Arial", 12))
    install_button.pack(pady=10)

    install_button = Button(root, text="Run game", command=run_launcher, font=("Arial", 12))
    install_button.pack(pady=10)

    log_frame = Scrollbar(root, orient=VERTICAL)
    log_frame.pack(side=RIGHT, fill=Y)


    log_window = Text(root, wrap="word", yscrollcommand=log_frame.set, height=15, width=70)
    log_window.pack(pady=10)
    log_window.insert(INSERT, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nLog:\n")
    log_frame.config(command=log_window.yview)
    log_window.config(state=DISABLED)

    install_button = Button(root, text="Report issues", command=report_issues, font=("Arial", 12))
    install_button.pack(pady=10)


    # Add an exit button
    exit_button = Button(root, text="Exit", command=root.quit, font=("Arial", 12))
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_installer()
