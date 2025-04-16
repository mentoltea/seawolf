# from logic import *
import logic

prelogic = logic.prelogic
common = logic.common
pygame = common.pygame
# import prelogic
# import pygame
# import common

def get_trans(Surf : pygame.Surface, width: float, height: float, angle: float):
    return pygame.transform.rotate(pygame.transform.scale(Surf, (int(round(width)), int(round(height)))), int(round(angle)))
    #return pygame.transform.scale(pygame.transform.rotate(Surf, int(round(angle))), (int(round(width)),int(round(height))))

def all_window_update():
    for button in common.active_buttons:
        button.draw(common.window)
    
    for label in common.active_labels:
        label.draw(common.window)
    
    
    if (common.active_dialog!=None):
        common.active_dialog.draw(common.window)
        
def all_window_postupdate():
    mb_y: float = 0
    for box in common.MBs:
        box.draw(common.window, 0, mb_y)
        mb_y += box.size_y+1

def main_menu_window_update():
    for i in range(0, prelogic.open_hosts_onepage):
        idx = prelogic.open_hosts_page*prelogic.open_hosts_onepage + i
        if (idx >= len(prelogic.open_hosts_buttons)): break
        
        button: logic.common.ButtonInteractive = prelogic.open_hosts_buttons[idx]
        button.draw(common.window)
    
    if (prelogic.open_hosts_page_label): 
        prelogic.open_hosts_page_label.draw(common.window)

def preparing_menu_window_update():
    pass

def game_menu_window_update():
    pass

def window_update():
    common.wn.fill((0,0,0))
    common.window.fill((245,245,245))
    
    
    all_window_update()
    match logic.game.gamestate:
        case logic.common.GameState.MAIN_MENU:
            main_menu_window_update()
        
        case logic.common.GameState.PREPARING_MENU:
            preparing_menu_window_update()
        
        case logic.common.GameState.GAME_MENU:
            game_menu_window_update()
        
        case _:
            pass
    all_window_postupdate()
    
    common.wn.blit(get_trans(common.window, common.RES_CURRENT[0], common.RES_CURRENT[1], 0), (0,0))

