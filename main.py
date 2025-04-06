from common import *
from game import *
from connection import *
from eventhandler import *

def all_update():
    for box in MBs:
        if (time.time() - box.created >= box.timeout):
                MBs.remove(box)

def main_menu_update():
    pass

def preparing_menu_update():
    pass

def game_menu_update():
    pass

def game_update():
    all_update()
    match gamestate:
        case GameState.MAIN_MENU:
            main_menu_update()
        
        case GameState.PREPARING_MENU:
            pass
        
        case GameState.GAME_MENU:
            pass