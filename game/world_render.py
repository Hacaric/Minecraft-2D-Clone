#from main import Point2d
import math
block_in_screenX = 12
window_width = 800
window_height = 600
block_size = window_width/block_in_screenX
class Point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

block_in_screenY = round(window_height/block_size)
block_multiplyer = 1
static_y_add = window_height/2

def get_screen_pos(camera: Point2d, point: Point2d) -> list[int, int, int]:
    x = (point.x*block_size - camera.x*block_size) * block_multiplyer
    y =  (point.y*block_size - camera.y*block_size) * block_multiplyer
    #print(x, y)
    size = block_size * block_multiplyer
    return [math.floor(x), math.floor(static_y_add-y), size+1]
def get_position(x, y):
    y = static_y_add - y
    
#print(", ".join(list(map(str, get_screen_pos(Point2d(0, 0), Point2d(0, 0))))))