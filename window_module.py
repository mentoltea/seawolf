# from logic import *
import logic
from logic import prelogic
from prelogic import ui
from prelogic import common
from prelogic import game
from common import pygame
# import prelogic
# import pygame
# import common

UNKNOWN = ui.WHITE
HIDDEN = (220, 220, 200)
EMPTY = (200, 200, 230)
BOAT = ui.LIGHTGRAY
SHOT = ui.LIGHTRED
KILLED = ui.RED



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

def choose_mode_menu_window_update():
    pass

def draw_gamemap(surf: pygame.Surface, x: int, y: int, tilesize: float, gamemap: list[list[int]]):
    font = ui.Font24
    for iy in range(10):
        letter = str(iy+1)
        (size_x, size_y) = font.size(letter) # type: ignore
        ui.draw_text(letter, x-size_x-5, y + iy*tilesize + (tilesize-size_y)/2, surf=surf, font=font)
    
    for ix in range(10):
        letter = game.ALPHABET[ix].upper()
        (size_x, size_y) = font.size(letter) # type: ignore
        ui.draw_text(letter, x + ix*tilesize + (tilesize-size_x)/2, y - size_y - 5, surf=surf, font=font)
    
    mouse_ipos = (
        int((common.mouse_pos[0]-x)//tilesize),
        int((common.mouse_pos[1]-y)//tilesize)
    )
    holding_pts: list[tuple[int, int]] = []
    (cx,cy) = mouse_ipos
    for _ in range(prelogic.holding_ship):
        holding_pts.append((cx, cy))
        if (prelogic.holding_orientation == 0):
            cx += 1
        else:
            cy += 1
    
    for iy in range(10):
        for ix in range(10):
            clr = ui.WHITE
            match (gamemap[iy][ix]):
                # 0 - unknown cell
                case game.CellType.UNKNOWN:
                    clr = UNKNOWN
                case game.CellType.HIDDEN:
                    clr = HIDDEN
                case game.CellType.EMPTY:
                    clr = EMPTY
                case game.CellType.BOAT:
                    clr = BOAT
                case game.CellType.SHOT:
                    clr = SHOT
                case game.CellType.KILLED:
                    clr = KILLED
                case _:
                    pass
            if ((ix, iy) == mouse_ipos or (ix,iy) in holding_pts):
                clr = tuple(map(lambda v: max(0, v-25), clr))
            pygame.draw.rect(surf, clr, pygame.Rect(x + ix*tilesize, y + iy*tilesize, tilesize, tilesize))
            pygame.draw.rect(surf, ui.BLACK, pygame.Rect(x + ix*tilesize, y + iy*tilesize, tilesize, tilesize), 1)

def preparing_menu_window_update():
    if (game.game):
        draw_gamemap(common.window, prelogic.editmap_pos[0], prelogic.editmap_pos[1], prelogic.editmap_tilesize, game.game.editmap)
    
    if (prelogic.holding_ship):
        if prelogic.holding_orientation==0:
            pygame.draw.rect(common.window, (255,0,0), (common.mouse_pos[0], common.mouse_pos[1], 20, 10))
        else:
            pygame.draw.rect(common.window, (255,0,0), (common.mouse_pos[0], common.mouse_pos[1], 10, 20))
            

def game_menu_window_update():
    if (game.game):
        draw_gamemap(common.window, *prelogic.mymap_pos, prelogic.mymap_tilesize, game.game.mymap)
        draw_gamemap(common.window, *prelogic.enemymap_pos, prelogic.enemymap_tilesize, game.game.enemymap)

def window_update():
    common.wn.fill((0,0,0))
    common.window.fill((245,245,245))
    
    
    all_window_update()
    match logic.game.gamestate:
        case common.GameState.CHOOSE_MODE_MENU:
            choose_mode_menu_window_update()
        
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

