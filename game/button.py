import pygame
from responses import action


class Button:
    def __init__(self, x:int, y:int, hitbox_width:int, hitbox_height:int, texture:pygame.Surface, hover_texture:pygame.Surface, title:str, return_value:any = action.button_pressed, texture_covers_button:bool=True, locked:bool=False, name:str=None):
        self.name = name if name else title
        self.x = x
        self.y = y
        self.width = hitbox_width
        self.height = hitbox_height
        self.rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        if texture_covers_button:
            self.texture = pygame.transform.scale(texture.copy(), (self.width, self.height))
            self.hover_texture = pygame.transform.scale(hover_texture.copy(), (self.width, self.height))
        else:
            self.texture = texture.copy()
            self.hover_texture = hover_texture.copy()
        self.title = title
        self.color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.Font(None, 32)
        self.return_value = return_value
        self.is_pressed = False
        self.is_hovered = False
        self.this_rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        self.locked:bool = locked
        self.loadFinalTextures()
    def loadFinalTextures(self):
        text_surface = self.font.render(self.title, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.button_surface = self.texture.copy()
        self.button_surface.blit(text_surface, text_rect)
        self.button_surface_hover = self.hover_texture.copy()
        self.button_surface_hover.blit(text_surface, text_rect)
    def tick(self, mouse_clicked, events, mouse_pos):
        if self.locked:
            return action.none
        # mouse_pos = pygame.mouse.get_pos()
        if self.this_rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False
        if self.is_hovered and mouse_clicked:
            return self.return_value
        return action.none
    def render(self, surface) -> None:
        surface.blit(self.button_surface if not self.is_hovered else self.button_surface_hover, self.rect)
    def changeTitle(self, newTitle):
        self.title = newTitle
        self.loadFinalTextures()