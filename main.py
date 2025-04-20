import window_module
from window_module import logic
from logic import prelogic
from logic import common
from common import pygame

try:
    1/0 # type: ignore
except Exception as e:
    prelogic.ERROR(str(e))



prelogic.LOGS_ENABLED = True

while common.RUN:
    common.clock.tick(common.FPS)
    # game.last_gamestate = game.gamestate
    
    common.mouse_clicked = False
    
    common.EVENTS = pygame.event.get()
    for event in common.EVENTS:
        if (event.type == pygame.QUIT):
            common.RUN = False
            logic.eventhandler.EventHandler.quit()
            break
        
        if (event.type == pygame.MOUSEBUTTONDOWN):
            common.mouse_clicked = True
            common.mouse_pos = pygame.mouse.get_pos()
            common.mouse_button = event.button
    
    
    logic.game_update()
    window_module.window_update()
    
    pygame.display.update()