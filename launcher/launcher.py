import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import json
import subprocess
import time

launcher_data_file = os.path.join(os.path.dirname( __file__ ), '.', 'laucher_config.json')

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 2D Launcher")
        self.root.geometry("600x400")

        self.setup_ui()

    def setup_ui(self):
        with open(launcher_data_file, "r") as file:
            data = json.load(file)
        self.version = data["version"]
        self.game_versions_names = list(data["game_versions"].keys())
        self.game_versions = data["game_versions"]
        game_version_last_played = data["game_version_last_played"]
        # Title Label
        title_label = ttk.Label(self.root, text="Minecraft 2D Launcher", font=("Arial", 18))
        title_label.pack(pady=10)

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

        # Auth Token
        auth_frame = ttk.LabelFrame(self.root, text="Authentication")
        auth_frame.pack(fill="x", padx=10, pady=10)

        self.auth_token_display = ScrolledText(auth_frame, height=3, wrap=tk.WORD)
        self.auth_token_display.pack(fill="x", padx=10, pady=5)
        
        auth_button = ttk.Button(auth_frame, text="Get Auth Token", command=self.get_auth_token)
        auth_button.pack(pady=5)

        # Launch Button
        launch_button = ttk.Button(self.root, text="Launch Game", command=self.launch_game)
        launch_button.pack(pady=20)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(pady=10)

    def get_auth_token(self):
        """ Placeholder for getting auth token. """
        messagebox.showinfo("Info", "Auth token functionality not implemented yet.")

    def download_version(self, version):
        """ Placeholder for downloading a game version. """
        pass

    def launch_game(self):
        selected_version = self.version_var.get()
        if selected_version:
            with open(launcher_data_file, "r+") as file:
                data = json.load(file)
                file.seek(0)
                data["game_version_last_played"] = self.game_versions_names.index(selected_version)
                json.dump(data, file)  
            if not "game" in os.listdir("./"):
                self.download_version(version=selected_version)
            self.status_var.set(f"Status: Launching version {selected_version}...")
            os.chdir(self.game_versions[selected_version])
            game_status = subprocess.Popen(["python", "./main.py"])
            self.status_var.set(f"Status: Game is running...")
            while game_status.poll() is None:
                time.sleep(1)
            self.status_var.set("Status: Ready")
            os.chdir(os.path.join(os.getcwd(), ".."))
        else:
            messagebox.showwarning("Warning", "No version selected!")

if __name__ == "__main__":
    # import time
    # def monitor_game(game_path, launcher_path):
    #     # Start the game
    #     game_process = subprocess.Popen([game_path])
        
    #     # Wait for the game to exit
    #     while game_process.poll() is None:
    #         time.sleep(1)
        
    #     # Relaunch the launcher
    #     subprocess.Popen()
    # monitor_game("path/to/game_executable", "path/to/launcher_script.py")
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
