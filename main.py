# import common
from window_module import *


# MBs.append(MessageBox("Test message for 5 seconds", 5, fontcolor=(255,0,0)))
# MBs.append(MessageBox("Test message for 2 seconds", 2))
# MBs.append(MessageBox("Test message for 3.5 seconds", 3.5, backcolor=(180,180,215)))
try:
    1/0
except Exception as e:
    ERROR(str(e))



common.LOGS_ENABLED = True

while common.RUN:
    clock.tick(FPS)
    # game.last_gamestate = game.gamestate
    
    common.mouse_clicked = False
    
    common.EVENTS = pygame.event.get()
    for event in common.EVENTS:
        if (event.type == pygame.QUIT):
            common.RUN = False
            eventhandler.EventHandler.quit()
            break
        
        if (event.type == pygame.MOUSEBUTTONDOWN):
            common.mouse_clicked = True
            common.mouse_pos = pygame.mouse.get_pos()
            common.mouse_button = event.button
    
    
    game_update()
    window_update()
    
    pygame.display.update()