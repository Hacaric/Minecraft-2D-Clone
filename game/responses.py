
class DynamicAttributes: #By ChatGPT
    def __init__(self, *args, name="unnamed"):
        self.name = name
        for arg in args:
            # if type(arg) == tuple:
            #     setattr(self, arg[0], *arg[1:])
            if isinstance(arg, str):
                setattr(self, arg, self.name + ":" + arg)
            else:
                setattr(self, str(arg), self.name + ":" + str(arg))

class Request:
    def __init__(self, type, *args, **kwargs):
        self.type = type
        self.args = args
        self.kwargs = kwargs
            
action = DynamicAttributes("close", "none", "button_pressed", "open", "command", "exec", "signal", name="action")

status = DynamicAttributes("error", "success", "none", "success_open", "terminate", "signal", name="status")
        
worldRequestTypes = DynamicAttributes("error", "getChunk", "updateChunk", "setLoadedChunks", name="worldRequest")

class gui_action:
    def __init__(self, action, *args, **kwargs):
        self.return_action = action
        if len(args) > 0:
            self.target = args[0]
        else:
            self.target = self.void
        if len(args) > 1:
            self.target_args = args[1:]
        else:
            self.target_args = []
        self.kwargs = dict(kwargs)
    def void(*_,**kw):pass
    def copy(self):
        return gui_action(self.return_action, self.target, *self.target_args, **self.kwargs) if self.target else gui_action(self.return_action, **self.kwargs)