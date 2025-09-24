class MenuClosed(Exception):
    pass
class FailedConnectingServer(Exception):
    pass
class ConnetionClosed(Exception):
    pass
class InvalidServerResponse(Exception):
    pass
class ErrorGettingSound(Exception):
    def play(*args):
        pass
class PlayerAlreadyExcist(Exception):
    pass
class PlayerNotExist(Exception):
    pass
class NotEnoughStates(Exception):
    pass
class InvalidState(Exception):
    pass
class InvalidPosition(Exception):
    def __init__(self, *args):
        if len(args) > 0:
            self.x = args[0]
        else:
            self.x = None
        if len(args) > 1:
            self.y = args[0]
        else:
            self.y = None
        self.args = args[2:]
INVALID_BLOCKS_POSITION = -10
WAITING_FOR_RESPONSE = -11
NOT_FOUND = -404
BLOCK_NOT_FOUND = -1
SUCCESS = 0