import sys
import os
print("Checking requirements...\n")
python_version = float(f"{sys.version_info.major}.{sys.version_info.minor}")

 
try:
    sys.stdout = open(os.devnull, 'w') 
    sys.stderr = open(os.devnull, 'w') 
    import pygame
    pygame_installed = True
except:
    pygame_installed = False
finally:
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__




try:
    sys.stdout = open(os.devnull, 'w') 
    import tk
    tk_installed = True
except:
    tk_installed = False
finally:
    sys.stdout = sys.__stdout__

print("Python version:", python_version, "-->", "required version is 3.10." if python_version < 3.10 else "version high enough.")
print("Pygame installed." if pygame_installed else "Pygame not installed. You can install it using 'pip install pygame'.")
print("Tkinter installed." if tk_installed else "Tkinter not installed. You can install it using 'pip install tk'.")


# print("\nOverview:\n", "All packages are installed. For game start run 'python ./launcher/launcher.py'." if pygame_installed and python_version >= 3.10 and tk_installed else (("Install python version 3.10 or higher." if python_version < 3.10 else "") + ("Install pygame: $pip install pygame" if not pygame_installed else "")))