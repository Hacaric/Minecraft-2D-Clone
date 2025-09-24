import pygame
class Text:
    def __init__(self, x:int, y:int, text:str, font_size:int = 12, font_name="monospace", bold:bool = False, font_color=(0,0,0)) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.font_color = font_color
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.font.set_bold(bold)
        self.text_surface = self.font.render(self.text, True, self.font_color)
    def tick(self, mouse_down, events, mouse_pos, new_text = None):
        if new_text != None:
            self.text = new_text
            self.text_surface = self.font.render(self.text[-self.max_chars:], True, self.font_color)
    def render(self, screen):
        screen.blit(self.text_surface, (self.x, self.y))
        
class TextInput:
    def __init__(self, x:int, y:int, width:int, height:int, texture, placeholder="", text="", clear_on_enter = False, font_size:int = 32, maxlen:int = 0, name:str=None, whitelist:list[str]="ALL") -> None:
        self.name = name if name!=None else placeholder
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
        self.default_placeholder_font_color = (50, 50, 50)
        self.gameTick = 0
        self.is_hovered = False
        self.whitelist = whitelist if not whitelist=="ALL" else None
        self.font = pygame.font.SysFont("monospace", self.font_size)
        self.font.set_bold(True)
        if maxlen == 0:
            self.max_chars = width//(self.font.size("W")[0])
        else:
            self.max_chars = maxlen#width//(font.size("W")[0])
    
    def get_collision(self, mousex: int, mousey: int, mouse_button_clicked: bool, collision_surface: list):
        if mouse_button_clicked:
            x, y, width, height = collision_surface
            if x <= mousex <= x + width and y <= mousey <= y + height:
                return True
        return False

    def tick(self, mouse_click, events, mouse_pos, return_text = False, ignore_input = False):
        self.gameTick = pygame.time.get_ticks()
        mouse_x, mouse_y = mouse_pos
        self.is_hovered = self.get_collision(mouse_x, mouse_y, True, [self.x, self.y, self.width, self.height])
        if self.is_hovered and mouse_click:
            self.active = True
        elif mouse_click:
            self.active = False
        if self.active:
            for event in events:
                if event.type == pygame.KEYDOWN and not ignore_input==True:
                    if event.key == pygame.K_RETURN:
                        copied_text = self.text
                        if self.clear_on_enter:
                            self.text = ""
                        self.active = False
                        return copied_text
                    elif event.key == pygame.K_BACKSPACE: 
                        self.text = self.text[:-1] 

                    else: 
                        if event.unicode.isprintable():
                            if self.whitelist is None or event.unicode in self.whitelist:
                                self.text += event.unicode            
        if return_text:
            return self.text
        return None
    
    def render(self, screen):
        screen.blit(self.texture, (self.x, self.y))
        if self.text != "":
            if self.gameTick % 1000 > 500 and self.active:
                text_surface = self.font.render((self.text[-self.max_chars:] + "|"), True, self.default_font_colour)
            else:
                text_surface = self.font.render(self.text[-self.max_chars:], True, self.default_font_colour)#-int(self.width/self.font_size)*2
        else:
            if self.active and self.gameTick % 1000 > 500:
                text_surface = self.font.render("|", True, self.default_font_colour)
            elif not self.active:
                text_surface = self.font.render(self.placeholder[:self.max_chars-1], True, self.default_placeholder_font_color)
            else:
                text_surface = self.font.render("", True, self.default_placeholder_font_color)
            # if len(self.text) < self.max_chars:
        #     adjustion = 0
        # else:
        #     adjustion = 0#((len(self.text)-self.max_chars)*self.font_size/3)
        screen.blit(text_surface, (self.x + 5, self.y + 5))


class margin:
    def __init__(self, left:int, top:int, right:int, bottom:int) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom