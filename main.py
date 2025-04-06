from window_module import *

# MBs.append(MessageBox("Test message for 5 seconds", 5, fontcolor=(255,0,0)))
# MBs.append(MessageBox("Test message for 2 seconds", 2))
# MBs.append(MessageBox("Test message for 3.5 seconds", 3.5, backcolor=(180,180,215)))
try:
    1/0
except Exception as e:
    ERROR(str(e))

while RUN:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            RUN = False
    
    game_update()
    window_update()
    
    pygame.display.update()