import sys
import os
python_version = float(f"{sys.version_info.major}.{sys.version_info.minor}")

 
try:
    sys.stdout = open(os.devnull, 'w') 
    import pygame
    pygame_installed = True
except:
    pygame_installed = False
finally:
    sys.stdout = sys.__stdout__


print("Python version:", python_version, "-->", "required version is 3.10." if python_version < 3.10 else "version high enough.")
print("Pygame not installed." if not pygame_installed else "Pygame installed.")

print("\nOverview:\n", "All packages are installed. For game start run 'main.py' file." if pygame_installed and python_version >= 3.10 else (("Install python version 3.10 or higher." if python_version < 3.10 else "") + ("Install pygame: $pip install pygame" if not pygame_installed else "")))