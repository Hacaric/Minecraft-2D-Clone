class Inventory:
    def __init__(self):
        self.main_inventory = [None] * 27
        self.hotbar = [None] * 9
        self.armor_slots = [None] * 4
        self.hotbar = ["grass", "dirt", "stone", "cobblestone", "sand", "plank", "glass", "wood", "leaves"]
    def get_hotbar_slots(self):
        return self.hotbar
    
    def get_slot(self, x, y):
        if y == 0 and 0 <= x < 9:
            return self.hotbar[x]
        elif y < 4 and 0 <= x < 9:
            return self.main_inventory[x + (y-1)*9]
        elif y == 4 and 0 <= x < 4:
            return self.armor_slots[x]
        else:
            raise ValueError("Invalid slot coordinates.", x, y)
    
    def get_slot_from_x(self, x):
        print(x)
        return self.get_slot(x%9, x//9)

    def set_slot(self, x, y, item_id):
        if y == 0 and 0 <= x < 9:
            self.hotbar[x] = item_id
        elif y == 4 and 0 <= x < 4:
            self.armor_slots[x] = item_id
        elif 1 <= y < 4 and 0 <= x < 9:
            index = (y - 1) * 9 + x
            self.main_inventory[index] = item_id
        else:
            raise ValueError("Invalid slot coordinates.", x, y)