from texture_loader import item_names
from item import *
import _config
import json

INVENTORY_PRESETS = [
        [Item(item_names.index(i)) for i in ["grass", "dirt", "stone", "cobblestone", "sand", "plank", "glass", "wood", "leaves"]] + [None for i in range(3*9 + 4)]
    ]
class Inventory:
    def __init__(self):
        self.slots = [None for i in range(4 * 9 + 4)]
        self.mouse_slot = None
        #Default hotbar: ["grass", "dirt", "stone", "cobblestone", "sand", "plank", "glass", "wood", "leaves"]
        self.mapping = {"hotbar":[i for i in range(9)], "main":[i+9 for i in range(3 * 9)], "armor":[i+4*9 for i in range(4)]}

    def get_hotbar_slots(self):
        return self.hotbar
    
    def get_slot(self, id):
        # print("Getting slot:", id)
        return self.slots[id]

    def set_slot(self, id, item:Item):
        # print(f"Setting slot {id}")
        self.slots[id] = item
        
    def load_preset(self, preset_id):
        if preset_id < len(INVENTORY_PRESETS):
            self.slots = INVENTORY_PRESETS[preset_id].copy()
        else:
            raise IndexError(f"Error in Inventory.load_preset(): preset id {preset_id} doesn't exit.")
    
    def pickup_item(self, item:Item):
        if item is None:
            return None
        # Pickup item - if can't pickup or can pick up only some of items, remaining items are returned
        for i, slot_item in enumerate(self.slots):
            if slot_item is None:
                self.slots[i] = item.copy()
                return None
            if item.item_id == slot_item.item_id:
                if item.amount + slot_item.amount > _config.Constants.Inventory.max_stack_size:
                    items_transferred = _config.Constants.Inventory.max_stack_size - slot_item.amount
                    slot_item.amount += items_transferred
                    item.amount -= items_transferred
                else:
                    slot_item.amount += item.amount
                    break
        if item.amount == 0:
            return None
        return item
    
    def parse(self) -> str:
        parsed_slots = []
        for item in self.slots:
            if item is None:
                parsed_slots.append(None)
            else:
                parsed_slots.append(item.parse())
        parsed_mouse_slot = None if self.mouse_slot is None else self.mouse_slot.parse()
        data = {"slots":parsed_slots,
                "mouse_slot":parsed_mouse_slot}
        return json.dumps(data)
    
    def load(self, data):
        data = json.loads(data)
        self.slots = []
        for parsed_item in data["slots"]:
            self.slots.append(loadParsedItem(parsed_item))
        self.mouse_slot = loadParsedItem(data["mouse_slot"])