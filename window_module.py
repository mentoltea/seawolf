from logic import *
from common import *

def get_trans(Surf, width, height, angle):
    return pygame.transform.rotate(pygame.transform.scale(Surf, (int(round(width)), int(round(height)))), int(round(angle)))
    #return pygame.transform.scale(pygame.transform.rotate(Surf, int(round(angle))), (int(round(width)),int(round(height))))

def all_window_update():
    for button in active_buttons:
        button.draw(window)

def all_window_postupdate():
    mb_y = 0
    for box in MBs:
        box.draw(window, 0, mb_y)
        mb_y += box.size_y+1

def main_menu_window_update():
    for i in range(0, open_hosts_onepage):
        idx = open_hosts_page*open_hosts_onepage + i
        if (idx >= len(open_hosts_buttons)): break
        
        button = open_hosts_buttons[idx]
        button.draw(window)

def preparing_menu_window_update():
    pass

def game_menu_window_update():
    pass

def window_update():
    wn.fill((0,0,0))
    window.fill((245,245,245))
    
    
    all_window_update()
    match game.gamestate:
        case common.GameState.MAIN_MENU:
            main_menu_window_update()
        
        case common.GameState.PREPARING_MENU:
            preparing_menu_window_update()
        
        case common.GameState.GAME_MENU:
            game_menu_window_update()
    all_window_postupdate()
    
    wn.blit(get_trans(window, RES_CURRENT[0], RES_CURRENT[1], 0), (0,0))

