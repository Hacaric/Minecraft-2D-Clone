# 
# To execute this file, double-click it or run the command: $ python installer.py
#
# If your Python installation cannot be executed this way, verify if Python is 
# installed correctly. Alternatively, update the variable below to match the command 
# used to run Python in your console (e.g., "python3" or a custom alias).
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
python_shell_command = "python"
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


import tkinter as tk
from tkinter import ttk, messagebox, filedialog, END
from tkinter.scrolledtext import ScrolledText
import os
import json
import subprocess
import time
import requests
from zipfile import ZipFile
import os
import shutil
import datetime

from typing import Final as const

launcher_config_file = os.path.join(os.path.dirname( __file__ ), 'launcher_config.txt')
launcher_data_template = '{"version": 1, "game_versions": {"latest": "./game/"}, "game_version_last_played": 0}'
launcher_data_file = os.path.join(os.path.dirname( __file__ ), 'launcher_data.json')
empty_version:const[str] = "0.0.0.0-snapshot"
logs = ""
def log(*args, **kwargs):
    global logs
    logs += " ".join(map(str, args)) + "\n"
    print(*args, **kwargs)
class Version:
    def __init__(self, info:str):
        #info format: {major}.{minor}.{micro}-{type}
        self.type:int = info.split("-")[-1] #release, snapshot, prerelease
        numeric = info.split("-")[0].split(".")
        if len(numeric) <= 3:
            self.major:int = 0
            self.minor:int = 0
            self.micro:int = 0
            self.commit:int = 0
            self.full_format:str = "0.0.0.0-snapshot"
        else:
            self.major:int = int(numeric[0])
            self.minor:int = int(numeric[1])
            self.micro:int = int(numeric[2])
            self.commit:int = int(numeric[3])
            self.full_format:str = info
    def iAmHigher(self, other, count_comit=False):
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.micro > other.micro:
                    return True
                elif self.micro == other.micro:
                    if self.commit > other.commit and count_comit:
                        return True
        return False
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
def load_config(config_file_name):
    # try:
        with open(config_file_name, "r") as file:
            data = file.read().split("\n")
        config = {}
        for line in data:
            try:
                if (not line.startswith("#")) and (line != ""):
                    config[line.split(":")[0]] = int(line.split(":")[1]) if line.split(":")[1].isdigit() else line.split(":")[1]
            except:
                pass
        return config
    # except Exception as e:
    #     log(f"Error loading config file: {e}")
    #     return None

def parse_config(config:dict):
    data = []
    for key in config.keys():
        data.append(f"{key}:{config[key]}")
    return "\n".join(data)

class GameLauncher:
    def __init__(self, root):
        self.config = load_config(launcher_config_file)
        log(type(self.config))
        log(self.config)
        os.chdir(os.path.join(os.path.dirname( __file__ )))
        self.root = root
        self.root.title("Minecraft 2D Launcher")
        self.root.geometry("700x480")

        self.setup_ui()

        new_version = self.checkForUpdates()
        if new_version:
            if messagebox.askyesno("Update available", f"New version available: {new_version.full_format}.\nDo you want to download it?"):
                self.download_update()
    def setup_ui(self):
        try:
            open(launcher_data_file, "r")
        except:
            with open(launcher_data_file, "w") as file:
                file.write(launcher_data_template)
        with open(launcher_data_file, "r") as file:
            data = json.load(file)
        self.version = data["version"]
        self.game_versions_names = list(data["game_versions"].keys())
        self.game_versions = data["game_versions"]
        game_version_last_played = data["game_version_last_played"]
        # Title Label
        title_label = ttk.Label(self.root, text="Minecraft 2D Launcher", font=("Arial", 18))
        title_label.pack(pady=10)



        # Auth Token
        auth_frame = ttk.LabelFrame(self.root, text="Authentication")
        auth_frame.pack(fill="x", padx=10, pady=10)

        self.auth_token_display = ScrolledText(auth_frame, height=3, wrap=tk.WORD)
        self.auth_token_display.pack(fill="x", padx=10, pady=5)
        self.auth_token_display.insert(tk.INSERT, "Authentication not functional yet")
        
        # auth_button = ttk.Button(auth_frame, text="Get Auth Token", command=self.get_auth_token)
        # auth_button.pack(pady=5)

        update_button = ttk.Button(self.root, text="Get Updates", command=self.make_update)
        update_button.pack(pady=5)

        # Version Selection
        version_frame = ttk.LabelFrame(self.root, text="Select Game Version")
        version_frame.pack(fill="x", padx=10, pady=10)

        self.version_var = tk.StringVar()
        self.version_dropdown = ttk.Combobox(
            version_frame, textvariable=self.version_var, state="readonly"
        )
        self.version_dropdown["values"] = [*self.game_versions_names]  # Example versions
        self.version_dropdown.pack(pady=5, padx=10)
        self.version_dropdown.current(game_version_last_played%(len(self.game_versions)+1))

        # Launch Button
        launch_button = ttk.Button(version_frame, text="Launch Game", command=self.launch_game)
        launch_button.pack(pady=20)

        launch_button = ttk.Button(self.root, text="Report issues", command=self.report_issues)
        launch_button.pack(pady=5)

        launch_button = ttk.Button(self.root, text="Setting", command=self.settings_window)
        launch_button.pack(pady=20)

        # launch_button = ttk.Button(self.root, text="Website", command=lambda:log("https://github.com/Hacaric/Minecraft-2D-Clone"))
        # launch_button.pack(pady=20)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(pady=10)
    def copy_to_clipboard(self, text):
        """Copy text to the clipboard."""
        try:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Keep the clipboard updated
        except Exception as e:
            pass
    def report_issues(self):
        self.copy_to_clipboard(logs)
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
            webbrowser.open(f"https://github.com/Hacaric/Minecraft-2D-Clone/issues/new?title=Automatic Issue Report&body=Log time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nLogs:\n{logs.replace("\n", "\n- ")}".replace(" ", "%20").replace("\n", "%0A"), new=2)

    def save_config(self):
        with open(launcher_config_file, "w") as file:
            file.write(parse_config(self.config))

    def settings_window(self):
        def destroy(save=True):
            if save:
                try:
                    self.config["fun"] = int(light_dark_var.get())
                except:pass
                try:
                    self.config["rate_this_feature"] = int(fps_limit_var.get())
                except:pass
                self.save_config()
            settings_window.destroy()
        settings_window = tk.Toplevel(self.root)
        settings_window.protocol("WM_DELETE_WINDOW", destroy)
        settings_window.title("Settings")
        settings_window.geometry("400x300")

        settings_frame = ttk.LabelFrame(settings_window, text="Settings")
        settings_frame.pack(padx=20, pady=20)

        # Ratio Settings
        ratio_frame = ttk.LabelFrame(settings_window, text="You will be able to 'set things' here!")
        ratio_frame.pack(padx=20, pady=20)

        # Dark/Light Mode
        light_dark_var = tk.IntVar()
        light_dark_var.set(int(self.config["fun"]))
        light_dark_checkbutton = ttk.Checkbutton(ratio_frame, text="Had fun?", variable=light_dark_var)
        light_dark_checkbutton.pack(pady=5)

        # FPS Limit
        fps_limit_var = tk.StringVar()
        fps_limit_var.set(self.config["rate_this_feature"])
        fps_limit_label = ttk.Label(ratio_frame, text="Rate this feature:")
        fps_limit_label.pack()
        fps_limit_entry = ttk.Entry(ratio_frame, textvariable=fps_limit_var, width=5)
        fps_limit_entry.pack(pady=5)

        cancel_button = ttk.Button(settings_window, text="Cancel", command=lambda:destroy(save=False))
        cancel_button.pack(pady=5)
        done_button = ttk.Button(settings_window, text="Done", command=destroy)
        done_button.pack(pady=5)

        # # Close Launcher when launching game
        # close_launcher_var = tk.IntVar()
        # close_launcher_var.set(int(self.config_data["close_launcher"]))
        # close_launcher_checkbutton = ttk.Checkbutton(ratio_frame, text="Close Launcher when launching game", variable=close_launcher_var, command=lambda: self.config_data["close_launcher"] = str(close_launcher_var.get()))
        # close_launcher_checkbutton.pack(pady=5)
        try:
            settings_window.mainloop()
        except:
            destroy(save=False)

    def make_update(self):
        # log("[Debug:143] self.auth_token_display.get('1.0', END):\n", self.auth_token_display.get("1.0", END).replace("\n", "*"), type(self.auth_token_display.get("1.0", END)))
        
        #TK puts \n at end of ScrolledText. That's reason for '[:-1]' down below vvvvvvvvvvvvvvvv
        if self.checkForUpdates(count_comit=True) == False and self.auth_token_display.get("1.0", END)[:-1]!="!force_update":
            messagebox.showwarning("Warning", f"Newest version already installed: {self.getCurrentVersion()}\n(You can bypass this by typing '!force_update' into auth box.)\nAborting.")
            return
        if messagebox.askokcancel("Update info", "Update will erase all data except for the 'saves' folder.\nDo you want to continue?"):
            # choice = messagebox.askquestion(
            #     "Directory Choice",
            #     "Do you want to choose a directory? Click 'Yes' to choose, 'No' to work with the current directory, or close to cancel.",
            # )
            # if choice is None:
            #     return
            # if choice == "yes":
            #     folder = filedialog.askdirectory(title="Choose")
            #     if folder:
            #         dir = folder
            # log(os.listdir(os.path.join(os.path.dirname(__file__), "../.update/")))
            # return
            self.download_update(os.path.join(os.path.dirname(__file__), "../"))
            messagebox.showinfo("Update info", "Update was downloaded\nRestarting launcher.")
            subprocess.Popen([python_shell_command, __file__])
            exit(0)
    def get_auth_token(self):
        """ Placeholder for getting auth token. """
        messagebox.showinfo("Info", "Auth token functionality not implemented yet.")

    # def download_version(self, version):
    #     """ Placeholder for downloading a game version. """
    #     pass

    def launch_game(self):
        selected_version = self.version_var.get()
        if selected_version:
            with open(launcher_data_file, "r+") as file:
                data = json.load(file)
                file.seek(0)
                data["game_version_last_played"] = self.game_versions_names.index(selected_version)
                json.dump(data, file)  
            # if not "game" in os.listdir("../"):
            #     self.download_version(version=selected_version)
            self.status_var.set(f"Status: Launching version {selected_version}...")
            os.chdir(os.path.join(os.path.dirname(__file__), "..", self.game_versions[selected_version]))
            game_status = subprocess.Popen([python_shell_command, "./main.py"])
            self.status_var.set(f"Status: Game is running...")
            while game_status.poll() is None:
                time.sleep(1)
            self.status_var.set("Status: Ready")
            os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
        else:
            messagebox.showwarning("Warning", "No version selected!")
    def checkForUpdates(self, count_comit=False):
        if "version.txt" in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")):
            current_version = Version(self.getCurrentVersion())
            latest_version = Version(self.getLatestCommitVersion())
            if latest_version.iAmHigher(current_version, count_comit=count_comit):
                return latest_version
            else:
                return False
        else:
            log(f"\n\n\nError looking for version.txt\nDirectory:{os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")}\n\n\n")
    def getCurrentVersion(self, gameDir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")):
        if os.path.exists(gameDir):
            if "version.txt" in os.listdir(gameDir):
                try:
                    with open(os.path.join(gameDir, "version.txt"), "r") as file:
                        return file.read()
                except Exception as e:
                    log("Error", e)
            else:
                with open(os.path.join(gameDir, "version.txt"), "w") as file:
                    file.write(empty_version)
                return empty_version
        else:
            return None
            
    def getLatestCommitVersion(self):
        url = "https://raw.githubusercontent.com/Hacaric/Minecraft-2D-Clone/refs/heads/main/version.txt"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                return response.content.decode("utf-8")
            except Exception as e:
                log(f"\nError accessing current version: {e}\n")
                return "0.0.0-snapshot"
        else:
            log('Failed to download file')
            exit(1)
    def download_update(self, directory:str=None):
        self.status_var.set(f"Status: Installing into directory: {directory if (not directory is None) else "idk"}")
        log(f"Status: Installing into directory: {directory if (not directory is None) else "idk"}")
        if directory is None:
            log("Directory is None :line140")
            directory = os.path.join(os.path.dirname(__file__), "..")
        update_zip_path = os.path.join(directory, '.update/version.zip')
        extract_path = os.path.join(directory, '.update/update_files/')
        extract_only_this_folder_from_zip = "./"
        old_files_path = os.path.join(directory)

        def folder_in_directory_tree(target_dir, folder_name):
            for item in [os.path.join(target_dir, folder) for folder in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, folder))]:
                if folder_name == os.path.basename(item):
                    return item
                addr = folder_in_directory_tree(item, folder_name)
                if addr:
                    return addr
            return False


        NOT_DELETE_DIR = ["saves"]

        # GitHub repository URL
        repository_name = 'Minecraft-2D-Clone'
        addr = f"https://github.com/Hacaric/{repository_name}/archive/refs/heads/main.zip"
        url = addr

        # Paths

        # Ensure directories exist
        os.makedirs(os.path.dirname(update_zip_path), exist_ok=True)
        os.makedirs(extract_path, exist_ok=True)
        os.makedirs(old_files_path, exist_ok=True)

        # Download the file
        self.status_var.set("Downloading update from github...")
        log("Downloading update from github...")
        response = requests.get(url)
        if response.status_code == 200:
            try:
                with open(update_zip_path, 'wb') as file:
                    file.write(response.content)
                log('File downloaded successfully')
            except Exception as e:
                log(f"\nError: {e}\n")
                return
        else:
            log('Failed to download file')
            exit(1)

        # Unzip the file
        self.status_var.set("Trying to unzip...")
        log("Trying to unzip...")
        try:
            with ZipFile(update_zip_path, 'r') as zObject:
                zObject.extractall(path=extract_path)
            log('Files unzipped successfully')
        except Exception as e:
            log(f'Failed to unzip files: {e}')
            exit(1)

        #Rename to repository name

        try:
            old_folder = extract_path + repository_name + "-main"
            new_folder = extract_path + repository_name
            if os.path.exists(new_folder):
                shutil.rmtree(new_folder) 
            os.rename(old_folder, new_folder)
        except Exception as e:
            log(f"Failed renaming directory {extract_path}{old_folder} to {repository_name} error: {e}")
            exit(1)
        # Delete the zip file
        self.status_var.set("Deleting zip...")
        log("Deleting zip...")
        os.remove(update_zip_path)
        log("\nUpdating files...")
        new_files = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
        for filename in new_files:
            log(f"|---Updating file {filename}")
            os.replace(
                os.path.join(extract_path, repository_name, extract_only_this_folder_from_zip, filename),
                os.path.join(old_files_path, filename)
                )
            #os.replace(f"{extract_path}{repository_name}/{filename}", old_files_path+filename)

        for file_name in NOT_DELETE_DIR:
            not_delete = folder_in_directory_tree(os.path.join(old_files_path), file_name)
            if not_delete and os.path.exists(not_delete):
                log(f"|---Not updating folder (deleting from downloaded files): {not_delete}.")
                file_to_delete = folder_in_directory_tree(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip), file_name)
                if file_to_delete:
                    shutil.rmtree(file_to_delete)
                else:
                    log(f"\nError looking for existing file {file_to_delete}\n")

        self.status_var.set("\nUpdating folders...")
        log("\nUpdating folders...")
        new_folders = [i for i in os.listdir(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip)) if not os.path.isfile(os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,i))]
        for folder_name in new_folders:
            if os.path.exists(os.path.join(old_files_path, folder_name)):
                log(f"|---Updating folder {os.path.join(old_files_path, folder_name)}")
                shutil.rmtree(os.path.join(old_files_path, folder_name))
            try:
                os.makedirs(os.path.join(old_files_path,folder_name))
            except:
                pass
            os.rename(
                os.path.join(extract_path,repository_name,extract_only_this_folder_from_zip,folder_name), 
                os.path.join(old_files_path,folder_name)

            )

        log("\nReplacing completed.")
        self.status_var.set("Cleaning up...")
        log("Cleaning up...")
        try: 
            try:
                shutil.rmtree(extract_path)
            except:
                pass
            os.makedirs(extract_path)
        except Exception as e:
            log(f"Failed cleaning, repository probably contained directory. Error: {e}")
            exit(1)
        self.status_var.set("\nUpdated successfully.")
        log("\nUpdated successfully.")



if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
