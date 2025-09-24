"""

This file catches old luanchers that arent updated properly (bug where launcher directory is excluded)

"""

import os
import sys
import requests
import subprocess

print("\n\nThis file doesnt run the game!! client.py does.\n\n")

print("The fact that this ran is probably caused by oudated launcher.\nUpdating launcher...")


REPOSITORY_USER_AND_NAME = "Hacaric/Minecraft-2D-Clone"
version_file_url = f"https://raw.githubusercontent.com/{REPOSITORY_USER_AND_NAME}/refs/heads/main/launcher/launcher.py"
print("Downloading luncher.py")
response = requests.get(version_file_url)
if response.status_code == 200:
    file_content = response.content.decode("utf-8")
else:
    print(f"Error: Failed to download launcher, HTTP status code: {response.status_code}")
    sys.exit(1)

print("Download successful.\nOverwriting launcher.py...")

# Construct absolute paths for robustness
current_script_dir = os.path.dirname(os.path.abspath(__file__))
launcher_dir = os.path.abspath(os.path.join(current_script_dir, '..', 'launcher'))
old_launcher_path = os.path.join(launcher_dir, "old_launcher.py")
launcher_path = os.path.join(launcher_dir, "launcher.py")

if not os.path.exists(launcher_path):
    print("Failed to find launcher.py. Exiting...")
    exit(1)

try:
    if os.path.exists(old_launcher_path):
        os.remove(old_launcher_path)
except OSError as e:
    print(f"Warning: Could not remove old_launcher.py: {e}")

try:
    if os.path.exists(launcher_path):
        os.rename(launcher_path, old_launcher_path)
except OSError as e:
    print(f"Error: Could not rename existing launcher.py. Is it in use or are permissions incorrect? {e}")
    sys.exit(1)

with open(launcher_path, "w") as f:
    f.write(file_content)
print("Update completed. Running launcher.py.")

subprocess.Popen([sys.executable, launcher_path])
sys.exit(0) # Exit this script after launching the new launcher