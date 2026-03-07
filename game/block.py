from texture_loader import BlockID
class Block:
    def __init__(self, id):
        if isinstance(id, Block):
            self.id = id.id
            self.breaking_progress = id.breaking_progress
        else:
            self.id = id
            self.breaking_progress = 0
