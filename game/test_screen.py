import pygame
import textinput

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Screen")


running = True
box = pygame.surface.Surface((200, 30))
box.fill((100, 100, 100, 100))
this_input = textinput.Input(100, 100, 200, 30, box, text = "")
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
    screen.fill((255, 255, 255))
    x = this_input.render(screen, events, True)
    if x:
        print(x)
    pygame.display.flip()

pygame.quit()
