import game # type: ignore
from game import ui
from game import connection
from game import common # type: ignore
from common import task
from common import pygame
import time
# connection = game.connection
# common = game.common
# task = common.task


def ERROR(message: str, duration: float=5):
    message = "ERROR: " + message
    ui.MBs.append(ui.MessageBox(message, duration, fontcolor=(255,0,0)))
    print(message)

LOGS_ENABLED = False

def LOG(message: str, duration: float=3):
    global LOGS_ENABLED
    message = "LOG: " + message
    if LOGS_ENABLED: 
        print(message)
        # ui.MBs.append(ui.MessageBox(message, duration, backcolor=(200,200,200)))
        
def INFO(message: str, duration: float=3):
    global LOGS_ENABLED
    message = "INFO: " + message
    ui.MBs.append(ui.MessageBox(message, duration))
# import common
# import tasks.task as task
# import eventhandler

def safesend(connection: connection.TCP_Sock | None, message: str | bytes) -> bool:
    if (connection == None):
        return False
    try:
        connection.send(message)
        return True
    except Exception as e:
        LOG("Unable to send message")
        print(str(e))
        return False


MYUSERNAME = connection.LOCAL_INFO[0]
MYADRRESS = [ip for ip in connection.LOCAL_INFO[2] if not ip.startswith("127.")]

print(MYADRRESS, MYUSERNAME)

UDP: connection.UDP_Sock | None = None
TCP: connection.TCP_Sock | None = None

ActiveConnection: connection.TCP_Sock | None = None
LastCheckedConnection: float = time.time()

return_state: str = common.GameState.CHOOSE_MODE_MENU

# MAIN MENU
sent_requests: list[str] = [] #adresses
open_hosts: list[str] = [] #adresses
open_hosts_buttons: list[ui.ButtonInteractive] = []
open_hosts_page_label: ui.Label | None = None
open_hosts_page = 0
open_hosts_onepage = 4
open_hosts_update_task: task.ThreadTask | None = None
open_hosts_selfhost_label = None
# ------------------

# PREPARE MENU
editmap_pos = (40, 40)
editmap_tilesize = 45
editmap_size = editmap_tilesize*10
editmap_mouse_ipos = (0,0)

ready_button: ui.ButtonInteractive | None = None
opponent_ready_label: ui.Label | None = None
ready_cooldown: float = 0
max_ready_cooldown: float = 2

current_ships = game.SHIPS_COUNT.copy()
current_ships_buttons: list[ui.ButtonInteractive] = []

# 0 - not holding
# number - ship with that length
holding_ship: int = 0
# 0 - horyzontal
# 1 - vertical
holding_orientation: int = 0
# ------------------

# GAME MENU
looking_game_results: bool = False

mymap_pos = (40, 40)
mymap_tilesize = 45
mymap_size = mymap_tilesize*10
mymap_mouse_ipos = (0,0)

enemymap_pos = (common.WIN_X - 40, 40)
enemymap_tilesize = 45
enemymap_size = enemymap_tilesize*10
enemymap_mouse_ipos = (0,0)

turn_label: ui.Label | None = None
my_left_label: ui.Label | None = None
enemy_left_label: ui.Label | None = None

deck_assets: list[ tuple[ pygame.Surface, pygame.Surface ] ] = []
deck_assets_loaded: bool = False

def load_assets():
    global deck_assets, deck_assets_loaded
    try:
        deck1_h = pygame.image.load("assets/decks/1-deck.png")
        deck1_v = pygame.transform.rotate(deck1_h, 90)
        
        deck2_h = pygame.image.load("assets/decks/2-deck.png")
        deck2_v = pygame.transform.rotate(deck2_h, 90)
        
        deck3_h = pygame.image.load("assets/decks/3-deck.png")
        deck3_v = pygame.transform.rotate(deck3_h, 90)
        
        deck4_h = pygame.image.load("assets/decks/4-deck.png")
        deck4_v = pygame.transform.rotate(deck4_h, 90)
        
        deck_assets.append( (deck1_h, deck1_v) )
        deck_assets.append( (deck2_h, deck2_v) )
        deck_assets.append( (deck3_h, deck3_v) )
        deck_assets.append( (deck4_h, deck4_v) )
        deck_assets_loaded = True
    except:
        deck_assets.clear()
        deck_assets_loaded = False

load_assets()