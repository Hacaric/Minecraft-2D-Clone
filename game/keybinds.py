import pygame

Keybinds = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_SPACE,
    "inventory": pygame.K_e,
    "pause": pygame.K_ESCAPE,
    "hotbar_1": pygame.K_1,
    "hotbar_2": pygame.K_2,
    "hotbar_3": pygame.K_3,
    "hotbar_4": pygame.K_4,
    "hotbar_5": pygame.K_5,
    "hotbar_6": pygame.K_6,
    "hotbar_7": pygame.K_7,
    "hotbar_8": pygame.K_8,
    "hotbar_9": pygame.K_9,
    "hotbar_0": pygame.K_0,
    "hotbar_scroll_up": pygame.K_PAGEUP,
    "hotbar_scroll_down": pygame.K_PAGEDOWN,
    "force_quit":pygame.K_SEMICOLON
}
    # up = pygame.K_w,
    # down = pygame.K_s,
    # left = pygame.K_a,
    # right = pygame.K_d,
    # jump = pygame.K_SPACE,
    # inventory = pygame.K_i,
    # pause = pygame.K_ESCAPE,
    # hotbar_1 = pygame.K_1,
    # hotbar_2 = pygame.K_2,
    # hotbar_3 = pygame.K_3,
    # hotbar_4 = pygame.K_4,
    # hotbar_5 = pygame.K_5,
    # hotbar_6 = pygame.K_6,
    # hotbar_7 = pygame.K_7,
    # hotbar_8 = pygame.K_8,
    # hotbar_9 = pygame.K_9,
    # hotbar_0 = pygame.K_0,
    # hotbar_scroll_up = pygame.K_PAGEUP,
    # hotbar_scroll_down = pygame.K_PAGEDOWN,
    # force_quit = pygame.K_SEMICOLON


# class Keybinds:
#     def __init__(self, config_file):
#         try:
#             self.mapping:dict = json.load(config_file)
#             for key in self.mapping:
#                 self.mapping[key] = 
#         except Exception as e: # you just lost the game
#             raise e # you just lost the game
#     def getKey()