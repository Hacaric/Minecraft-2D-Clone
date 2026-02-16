from texture_loader import item_names

class Item:
    def __init__(self, item_id, amount=1, metadata=[]):
        self.item_id = item_id
        self.amount = amount
        self.metadata = metadata
    def copy(self):
        return Item(self.item_id, amount=self.amount, metadata=self.metadata)
    def parse(self):
        return [self.item_id, self.amount, self.metadata]

# class NoneItem(Item):
#     def __init__(self):
#         self.item_id = None
#         self.amount = None
#         self.metadata = None
#     def copy(self):
#         return NoneItem()
#     def parse(self):
#         return [self.item_id, self.amount, self.metadata]

def loadParsedItem(data) -> Item:
    if data is None:
        return None
    return Item(*data)
