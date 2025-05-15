import window_module
from window_module import logic
from logic import prelogic # type: ignore
from logic import common
from common import pygame


prelogic.LOGS_ENABLED = False
tick = 0

while common.RUN:
    common.clock.tick(common.FPS)
    tick = (tick + 1) % common.FPS
    # game.last_gamestate = game.gamestate
    
    common.mouse_button_down = False
    common.mouse_button_up = False
    common.mouse_wheel_up = False
    common.mouse_wheel_down = False
    common.mouse_pos = pygame.mouse.get_pos()
    common.EVENTS = pygame.event.get()
    for event in common.EVENTS:
        if (event.type == pygame.QUIT):
            common.RUN = False
            logic.eventhandler.EventHandler.quit()
            break
        
        if (event.type == pygame.MOUSEBUTTONDOWN):
            common.mouse_button_down = True
            common.mouse_button_up = False
            common.mouse_pos = pygame.mouse.get_pos()
            common.mouse_button = event.button
        elif (event.type == pygame.MOUSEBUTTONUP):
            common.mouse_button_down = False
            common.mouse_button_up = True
            common.mouse_pos = pygame.mouse.get_pos()
            common.mouse_button = event.button
        
        if (event.type == pygame.MOUSEWHEEL):
            if (event.y > 0):
                common.mouse_wheel_up = True
                common.mouse_wheel_down = False
            elif (event.y < 0):
                common.mouse_wheel_up = False
                common.mouse_wheel_down = True
    
    
    logic.game_update()
    window_module.window_update()
    
    pygame.display.update()