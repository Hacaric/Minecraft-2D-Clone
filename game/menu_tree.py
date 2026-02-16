import pygame
from button import Button
from textinput import TextInput, Text
from switch_button import SwitchButton
from responses import action, status, gui_action
from security import verifyExpression
def getSelections(text: str, startChar="<", endChar=">") -> list[str]:
    selections = []
    currStart = None
    for i in range(len(text)):
        if text[i] == startChar and currStart is None:
            currStart = i + 1
        elif text[i] == endChar and currStart is not None:
            selections.append(text[currStart:i])
            currStart = None
    return selections
def evaluateExpression(obj, tree, action_:gui_action, self_):
    print("Evaluating ", action_.target)
    CHAR_START = "<"
    CHAR_END = ">"
    action = action_.copy()
    eval_content = {"parent":obj, "tree":tree, "self":self_}
    try:
        newargs = list(action.target_args)
        for idx, arg in enumerate(action.target_args):
            expressions = getSelections(arg, CHAR_START, CHAR_END)
            for expression in expressions:
                try:
                    evaluated_result = eval(expression, eval_content)
                    newargs[idx]=action.target_args[idx].replace(f"{CHAR_START}{expression}{CHAR_END}", str(evaluated_result))
                except Exception as e:
                    print(f"Error occurred while evaluating expression: {expression}\nError: {e}")
        action.target_args = newargs
    except Exception as e:
        print("Error evaluating target_args expression:", e)

    try:
        for key, value in action.kwargs.items():
            expressions = getSelections(value, CHAR_START, CHAR_END)
            for expression in expressions:
                try:
                    evaluated_result = eval(expression, eval_content)
                    action.kwargs[key] = value.replace(f"{CHAR_START}{expression}{CHAR_END}", str(evaluated_result))
                except Exception as e:
                    print(f"Error occurred while evaluating expression: {expression}\nError: {e}")
    except Exception as e:
        print("Error evaluating kwargs expression:", e)
    return action
gui_action_none = gui_action(action.none)
class Menu:
    def __init__(self, name:str, gui_input:list[Button|TextInput|SwitchButton], gui_actions:list[gui_action], background:(pygame.Surface|None), background_by_reference:bool = False):
        self.name = name
        self.gui_input = gui_input
        self.gui_actions = gui_actions
        self.new_background = None
        self.background_by_reference = background_by_reference
        self.original_background = background
        self.background_id = id(background)
        if background and not self.background_by_reference:
            self.background = background.copy()
        else:
            self.background = background
        self.esc_action = gui_action(action.close)
        self.tree = None

    def render(self, screen) -> None:
        if self.new_background and not self.background_by_reference:
            self.background = self.new_background.copy()
            self.original_background = self.new_background.copy()
            self.new_background = None

        if self.background:
            # print("BACKGROUND", self.name, self.background, id(self.background))
            screen.blit(self.background, (0, 0))
        for i in self.gui_input:
            i.render(screen)

    def tick(self, mouse_down, events, mouse_pos, keys) -> gui_action:
        if not self.background_by_reference and self.background_id != id(self.original_background):
            self.background = self.original_background.copy()
        if keys[pygame.K_ESCAPE]:
            return self.esc_action
        actions = []
        for i in self.gui_input:
            actions.append(i.tick(mouse_down, events, mouse_pos))
        actions_valid = [(i, actions[i]) for i in range(len(actions)) if actions[i] == action.button_pressed] # list[index_of_button (!= action.none)]
        if len(actions_valid) > 0:
            return evaluateExpression(self, self.tree, self.gui_actions[actions_valid[0][0]], self.gui_input[actions_valid[0][0]])
        return gui_action_none
    def getIdxByName(self, name:str) -> (int|None):
        """
        Returns a index of first gui component with specifyed name.    
        Returns None if not found.\n
        :name (str) - specify name of gui conponent from Menu.gui_input[]
        """
        for idx, guiConpnent in enumerate(self.gui_input):
            if guiConpnent.name == name:
                return idx
        return None
    def resize(self, newsize:tuple[int, int]):
        if self.original_background and not self.background_by_reference:
            self.background = pygame.transform.scale(self.original_background, newsize)
    def changeBackground(self, background:pygame.Surface):
        self.new_background = background
        self.original_background = background
class TreeNode:
    def __init__(self, value:any, parent:int) -> None:
        self.parent:int = parent
        self.value:Menu = value
        self.children = []

    def add_child(self, child:int) -> None:
        self.children.append(child)

    def remove_child(self, child:int) -> None:
        self.children.remove(child)

class Trees:
    def __init__(self, *nodes:tuple[any, (str|int)]) -> None:
        self.nodes:list[TreeNode] = []
        self.names = []
        self.is_empty = True
        for node in nodes:
            self.add(*node)
    def add(self, value:Menu, parent:(str|int)) -> str:
        if type(parent) == str:
            try:
                parent_index = self.find(parent)
            except:
                return status.error
        else:
            parent_index = parent
        self.is_empty = False
        node = TreeNode(value, parent_index)
        self.names.append(value.name)
        self.nodes.append(node)
        if not parent_index is None:
            self.nodes[parent_index].add_child(len(self.nodes)-1)
        return status.success

    def read(self):
        return [[self.nodes[j].value for j in i.children] for i in self.nodes]

    def find(self, name:str) -> int:
        """
        Find menu with name in menu tree and returns its index.
        Raises error if not found.
        """
        return self.names.index(name)
    def get(self, index:int|str) -> TreeNode:
        """
        Find menu with name(str) or index(int) in menu tree and returns it.
        Raises error if not found.
        """
        if type(index) == str:
            return self.nodes[self.find(index)].value
        return self.nodes[index].value

    def remove(self, name:str|int) -> any:
        item_index = self.find(name) if type(name) == str else name
        self.nodes[item_index].parent.remove_child(item_index)
        self.names[item_index] = None
        return self.nodes[item_index].value

    def get_parent(self, name:str|int) -> (int|None):
        item_index = self.find(name) if type(name) == str else name
        return self.nodes[item_index].parent

class MenuCollection:
    def __init__(self, menus_tree:Trees, currenrMenuName:str=None, currentMenuIdx:int=None):
        self.tree = menus_tree if menus_tree.nodes else exit(Exception("Empty tree"))
        self.current_menu_idx = currentMenuIdx if (not currentMenuIdx is None) else (self.tree.find(currenrMenuName) if currenrMenuName else 0)
        self.screen_size:tuple[int, int] = None
        self.setTreeForMenus(self.tree)
    def resize(self, newSize):
        for node in self.tree.nodes:
            node.value.resize(newSize)
    def setTreeForMenus(self, tree):
        for node in self.tree.nodes:
            node.value.tree = tree
    def render(self, screen:pygame.Surface) -> None:
        self.tree.get(self.current_menu_idx).render(screen)
        # if self.screen_size is None:
        #     self.screen_size = screen.get_size()
        # if resized:
        #     self.screen_size = new_size
        #     for node in self.tree.nodes:
        #         node.value.resize(new_size)
        # else:
        #     if self.screen_size == screen.get_size():
        #         self.tree.get(self.current_menu).render(screen)
        #     else:
        #         print("ERROR:116:menu_tree.py")

    def tick(self, mouse_down, events, mouse_pos, keys) -> str:
        # pygame.mouse.set_cursor(pygame.cursors.arrow)
        current_action:gui_action = self.tree.nodes[self.current_menu_idx].value.tick(mouse_down, events, mouse_pos, keys)
        # if current_action != action.none:
        #     print("DEBUG:97:current_action", current_action, ";target", target)
        match current_action.return_action:
            case action.none:
                pass
            case action.close:
                try:
                    self.current_menu_idx = self.tree.nodes[self.current_menu_idx].parent
                except Exception as e:
                    print("DEBUG:menu_tree:188:error", e)
                    return status.error
                #print("current2:action.close;selected", self.selected)
                if self.current_menu_idx is None:
                    self.current_menu_idx = 0
                    # print("DEBUG:121")
                    return status.terminate
                # print("DEBUG:123")
            case action.open:
                self.current_menu_idx = self.tree.find(current_action.target) if type(current_action.target)==str else current_action.target
                return status.success_open
            case action.command:
                current_action.target(*current_action.target_args,**current_action.kwargs,)
            case action.exec:
                exec_content = {"parent":self.tree.nodes[self.current_menu_idx].value, "tree":self.tree}
                exec(current_action.target, exec_content)
                return status.success
            case action.signal:
                return status.signal
        return None

class GuiHandler:
    def __init__(self, menu_collection:MenuCollection) -> None:
        self.menu_collection = menu_collection

    def tick(self, mouse_down, events, mouse_pos, keys) -> str:
        rn = self.menu_collection.tick(mouse_down, events, mouse_pos, keys)
        if rn == status.error:
            return status.none
        return rn

    def render(self, screen:pygame.Surface) -> None:
        self.menu_collection.render(screen)
    def resize(self, newSize:tuple[int, int]):
        self.menu_collection.resize(newSize)
def defaultGameGuiHandler(windowWidth, windowHeight, gui_textures, setflag, currentMenuIdx=None, currenrMenuName=None):
    button_texture, button_hover_texture = gui_textures["button"], gui_textures["button_hover"]
    GUI_LARGE_BUTTON_WIDTH = 400
    GUI_SMALL_BUTTON_WIDTH = 195
    GUI_BUTTON_HEIGHT = 50
    FILENAME_LEGAL_CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-. !#$%&'()+,@[]^`{}~")
    NUMBER_CHARS = list("0123456789")

    variable_backgrounds = [pygame.Surface((windowWidth, windowHeight))]
    print(f"VAR_BACKGROUND, {id(variable_backgrounds[0])}")
    handler = GuiHandler(
        MenuCollection(
            Trees(
                (
                    Menu(
                        "Main", 
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Singleplayer"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Multiplayer", locked=False),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Quit")
                        ],
                        [
                            gui_action(action.open, "Singleplayer"),
                            gui_action(action.open, "Multiplayer"),
                            gui_action(action.close)
                        ],
                            gui_textures["main_menu_background"]
                    ),
                #  vvvvvv Parent
                    None
                ),
                (
                    Menu(
                        "Singleplayer", 
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Create new world"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Load world"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back")
                        ],
                        [
                            gui_action(action.open, 2),
                            gui_action(action.open, 4),
                            gui_action(action.close)
                        ],
                            gui_textures["main_menu_background"]
                    ),
                    "Main"
                ),
                (
                    Menu(
                        "New world", 
                        [
                            Button(windowWidth//2+5, windowHeight//2+90, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Create new world"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back"),
                            TextInput(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, name="worldNameInput",placeholder="Enter world name", whitelist=FILENAME_LEGAL_CHARS),
                            SwitchButton(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+30, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, ["Survival", "Creative"], 0, name="gamemodeSwitch", return_data=[1, 0]),
                            Button(windowWidth//2+5, windowHeight//2+30, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "More Options"),
                        ],
                        [
                            gui_action(action.command, setflag, "newWorld", name="<parent.gui_input[parent.getIdxByName('worldNameInput')].text>", gamemode="<parent.gui_input[parent.getIdxByName('gamemodeSwitch')].current_state>", seed="<tree.get(tree.find('Create World Options')).gui_input[tree.get('Create World Options').getIdxByName('seedInput')].text>"),
                            gui_action(action.close),
                            gui_action(action.none),
                            gui_action(action.none),
                            gui_action(action.open, 3)
                        ],
                            gui_textures["main_menu_background"]
                    ),
                    "Singleplayer"
                ),
                (
                    Menu(
                        "Create World Options",
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back"),
                            TextInput(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, name="seedInput",placeholder="Seed", whitelist=NUMBER_CHARS),
                        ],
                        [
                            gui_action(action.close),
                            gui_action(action.none),
                        ],
                            gui_textures["main_menu_background"]
                    ),
                    "New world"
                ),
                (
                    Menu(
                        "Load World",
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Load from file..."),
                        ],
                        [
                            gui_action(action.close),
                            gui_action(action.command, setflag, "loadWorld"),
                        ],
                        gui_textures["main_menu_background"]
                    ),
                    "Singleplayer"
                ),
                (
                    Menu(
                        "Multiplayer",
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Connect server", name="connectBtn"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-30, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Default", name="defaultIP"),
                            TextInput(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, "Enter IP address", text="", name="inputIP"),
                        ],
                        [
                            gui_action(action.close),
                            #                                                           vvvvv Evaluated in evaluateExpression() function vvvvvv
                            gui_action(action.command, setflag, "connectServerFullIP", "<parent.gui_input[parent.getIdxByName('inputIP')].text>"),
                            gui_action(action.exec, "parent.gui_input[parent.getIdxByName('inputIP')].text='127.0.0.1:1234'"),
                            gui_action(action.none),
                        ],
                        gui_textures["main_menu_background"]
                    ),
                    "Main"
                ),
                (
                    Menu(
                        "Connecting",
                        [
                            Text(windowWidth//2, windowHeight//2, "Connecting to the world...", font_size=60, bold=True)
                        ],
                        [
                            gui_action(action.none)
                        ],
                        gui_textures["main_menu_background"]
                    ),
                    "Singleplayer"
                ),
                (
                    Menu(
                        "Game",
                        [
                            Text(windowWidth//2, windowHeight-10, "Game", font_size=60, bold=True)
                        ],
                        [
                            gui_action(action.none)
                        ],
                        None
                    ),
                    "Singleplayer"
                ),
                (
                    Menu(
                        "Pause_menu",
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-120, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Back to game"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2-60, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Options"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Exit to main menu"),
                        ],
                        [
                            gui_action(action.close),
                            gui_action(action.open, "Pause_menu_options"),
                            gui_action(action.signal)
                        ],
                        variable_backgrounds[0],
                        background_by_reference=True
                    ),
                    None
                ),
                (
                    Menu(
                        "Pause_menu_options",
                        [
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+90, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Done"),
                            Button(windowWidth//2-GUI_LARGE_BUTTON_WIDTH//2, windowHeight//2+5, GUI_LARGE_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, button_hover_texture, "Apply"),
                            TextInput(windowWidth//2-GUI_SMALL_BUTTON_WIDTH//2, windowHeight//2-90, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, "TPS", text="", name="TPS_setter"),
                            TextInput(windowWidth//2-GUI_SMALL_BUTTON_WIDTH//2, windowHeight//2-160, GUI_SMALL_BUTTON_WIDTH, GUI_BUTTON_HEIGHT, button_texture, "FPS", text="", name="FPS_setter"),
                        ],
                        [
                            gui_action(action.close),
                            gui_action(action.command, setflag, "changeSettings", TPS="<parent.gui_input[parent.getIdxByName('TPS_setter')].text>", None_="<parent.gui_input[parent.getIdxByName('TPS_setter')].text=''>"),
                            gui_action(action.none),
                            gui_action(action.none),
                        ],
                        variable_backgrounds[0],
                        background_by_reference=True
                    ),
                    "Pause_menu"
                )
            ), currentMenuIdx=currentMenuIdx, currenrMenuName=currenrMenuName
        )
    )
    handler.resize((windowWidth, windowHeight))
    return handler