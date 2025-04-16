import window_module
# import common
# import prelogic
# import logic
# import messages

common = window_module.common
logic = window_module.logic
prelogic = logic.prelogic
messages = logic.messages
pygame = window_module.pygame

try:
    1/0 # type: ignore
except Exception as e:
    common.ERROR(str(e))



common.LOGS_ENABLED = True

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