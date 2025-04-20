# from logic import *
import logic
from logic import prelogic
from prelogic import ui
from prelogic import common
from common import pygame
# import prelogic
# import pygame
# import common

def get_trans(Surf : pygame.Surface, width: float, height: float, angle: float):
    return pygame.transform.rotate(pygame.transform.scale(Surf, (int(round(width)), int(round(height)))), int(round(angle)))
    #return pygame.transform.scale(pygame.transform.rotate(Surf, int(round(angle))), (int(round(width)),int(round(height))))

def all_window_update():
    for button in ui.active_buttons:
        button.draw(common.window)
    
    for label in ui.active_labels:
        label.draw(common.window)
    
        
def all_window_postupdate():
    mb_y: float = 0
    for box in ui.MBs:
        box.draw(common.window, 0, mb_y)
        mb_y += box.size_y+1
    if (ui.active_dialog!=None):
        ui.active_dialog.draw(common.window)

def main_menu_window_update():
    for i in range(0, prelogic.open_hosts_onepage):
        idx = prelogic.open_hosts_page*prelogic.open_hosts_onepage + i
        if (idx >= len(prelogic.open_hosts_buttons)): break
        
        button: ui.ButtonInteractive = prelogic.open_hosts_buttons[idx]
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

