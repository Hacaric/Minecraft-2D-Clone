import pygame

class Button:
    def __init__(self, x, y, width, height, texture, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.texture = texture
        self.hover_texture = pygame.image.load("assets/textures/GUI/button_hover.png")
        self.text = text
        self.color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.Font(None, 32)
        self.is_pressed = False

    def render(self, surface, mouse_clicked, x=None, y=None, text=None, width=False, height=False):
        if text is None:
            thistext = self.text
        else:
            thistext = text
        if x is None:
            dx = self.rect.x
        else:
            dx = x
        if y is None:
            dy = self.rect.y
        else:
            dy = y
        if width is False:
            dwidth = self.rect.width
        else:
            dwidth = width
        if height is False:
            dheight = self.rect.height
        else:
            dheight = height
        thisrect = pygame.Rect(dx, dy, dwidth, dheight)
        button_surface = pygame.Surface((dwidth, dheight))
        mouse_pos = pygame.mouse.get_pos()

        if thisrect.collidepoint(mouse_pos):
            current_texture = self.hover_texture
        else:
            current_texture = self.texture

        if current_texture:
            texture_rect = current_texture.get_rect()
            scaled_texture = pygame.transform.scale(current_texture, (dwidth, dheight))
            button_surface.blit(scaled_texture, (0, 0))
        else:
            button_surface.fill(self.color)
        text_surface = self.font.render(thistext, True, self.text_color)
        text_rect = text_surface.get_rect(center=(dwidth // 2, dheight // 2))
        button_surface.blit(text_surface, text_rect)
        surface.blit(button_surface, thisrect)

        self.is_pressed = thisrect.collidepoint(mouse_pos) and mouse_clicked
        # if self.is_pressed:
        #     print("hi I am pressed", mouse_pos)
        return self.is_pressed

    # def is_button_pressed(self):
    #     """Returns True if the button is currently pressed, otherwise False."""
    #     return self.is_pressed

