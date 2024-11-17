from button import Button
import gameExceptions
class SwitchButton:
    def __init__(self, x, y, width, height, texture, states:list[str], current_state:int=0, return_data:list=None):
        try:
            self.button = Button(x, y, width, height, texture, states[current_state])
        except:
            current_state = 0
            self.button = Button(x, y, width, height, texture, "error")
            self.current_state = current_state
            self.states = states
            raise gameExceptions.NotEnoughtStates()
        self.current_state = current_state
        self.states = states
        self.return_data = return_data
    def render(self, surface, mouse_clicked, x = None, y = None, width = False, height = False):
        if self.button.render(surface, mouse_clicked, x=x, y=y, width=width, height=height):
            self.current_state = (self.current_state + 1) % len(self.states)
            self.button.text = self.states[self.current_state]
        if self.return_data != None:
            return self.return_data[self.current_state]
        return self.states[self.current_state]
    def getstate(self)->any:
        if self.return_data != None:
            return self.return_data[self.current_state]
        return self.states[self.current_state]