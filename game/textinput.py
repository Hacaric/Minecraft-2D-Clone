import pygame
class TextInput:
    def __init__(self, x:int, y:int, width:int, height:int, texture, placeholder="", text="", clear_on_enter = False, font_size:int = 16, maxlen:int = 0) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.placeholder = placeholder
        self.text = text
        self.texture = pygame.transform.scale(texture, (self.width, self.height))
        self.clear_on_enter = clear_on_enter
        self.font_size = font_size
        self.active = False
        self.default_font_colour = (0, 0, 0)
        self.default_placeholder_font_colour = (50, 50, 50)
        if maxlen == 0:
            font = pygame.font.SysFont("monospace", self.font_size)
            font.set_bold(True)
            self.max_chars = width//(font.size("W")[0])
        else:
            self.max_chars = maxlen#width//(font.size("W")[0])
    
    def get_collision(self, mousex: int, mousey: int, mouse_button_clicked: bool, collision_surface: list):
        if mouse_button_clicked:
            x, y, width, height = collision_surface
            if x <= mousex <= x + width and y <= mousey <= y + height:
                return True
        return False

    def render(self, screen:pygame.Surface, events, collision:list[int, int, bool] = None, return_text = False):
        tick = pygame.time.get_ticks()
        if collision != None:
            mouse_x, mouse_y, mouse_click = collision
            if self.get_collision(mouse_x, mouse_y, mouse_click, [self.x, self.y, self.width, self.height]):
                self.active = True
            elif mouse_click:
                self.active = False
        #print(tick)
        if self.active:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        copied_text = self.text
                        if self.clear_on_enter:
                            self.text = ""
                        active = False
                        return copied_text
                    elif event.key == pygame.K_BACKSPACE: 
                        # get text input from 0 to -1 i.e. end. 
                        self.text = self.text[:-1] 

                    # Unicode standard is used for string 
                    # formation 
                    else: 
                        if event.unicode.isprintable():
                            self.text += event.unicode            
        screen.blit(self.texture, (self.x, self.y))
        font = pygame.font.SysFont("monospace", self.font_size)
        font.set_bold(True)
        if self.text != "":
            if tick % 1000 > 500 and self.active:
                text_surface = font.render((self.text[-self.max_chars:] + "|"), True, self.default_font_colour)
            else:
                text_surface = font.render(self.text[-self.max_chars:], True, self.default_font_colour)#-int(self.width/self.font_size)*2
        else:
            if self.active:
                if tick % 1000 > 500:
                    text_surface = font.render("|", True, self.default_font_colour)
            else:
                text_surface = font.render(self.placeholder[:self.max_chars-1], True, self.default_placeholder_font_colour)
            # if len(self.text) < self.max_chars:
        #     adjustion = 0
        # else:
        #     adjustion = 0#((len(self.text)-self.max_chars)*self.font_size/3)
        try:
            screen.blit(text_surface, (self.x + 5, self.y + 5))
        except UnboundLocalError:
            pass
        if return_text:
            return self.text
    
        return None
        #return self.text