from button import Button
import gameExceptions
class SwitchButton:
    def __init__(self, x:int, y:int, width:int, height:int, texture, hover_texture, states:list[str], current_state:int=0, return_data:list=None, name:str=None)->None:
        self.name = name if name else states[current_state]
        try:
            self.button = Button(x, y, width, height, texture, hover_texture, states[current_state], "Clicked")
        except:
            current_state = 0
            self.button = Button(x, y, width, height, texture, hover_texture, "error")
            self.current_state = current_state
            self.states = states
            raise gameExceptions.NotEnoughStates()
        self.current_state = current_state
        self.states = states
        self.return_data = return_data
    def render(self, surface)->any:
        self.button.render(surface)
    def tick(self, mouse_clicked, events, mouse_pos):
        changed_mode = self.button.tick(mouse_clicked, events, mouse_pos) == "Clicked"
        if changed_mode:
            self.current_state = (self.current_state + 1) % len(self.states)
            self.button.changeTitle(self.states[self.current_state])
        if self.return_data != None:
            return [changed_mode, self.return_data[self.current_state]]
        return [changed_mode, self.states[self.current_state]]
    def getstate(self)->any:
        if self.return_data != None:
            return self.return_data[self.current_state]
        return self.states[self.current_state]