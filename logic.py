import common
# from common import *
import tasks.task as task
import game
# from game import *
import connection
# from connection import *
import eventhandler
# from eventhandler import *

UDP: connection.UDP_Sock = None

open_hosts: list[tuple[str, str]] = []
open_hosts_buttons: list[common.ButtonInteractive] = []

open_hosts_update_task: task.ThreadTask = None

def open_hosts_update_func():
    global open_hosts_update_task
    while (game.gamestate == common.GameState.MAIN_MENU and UDP!=None):
        rcv = UDP.recv(2)
        if (rcv):
            (data, addr) = rcv
            jsondata = common.json.loads(data)
            # common.LOG(addr[0] + ": " +common.json.dumps(jsondata))
    open_hosts_update_task = None


def all_update():
    mb_y = 0
    for box in common.MBs:
        if ((common.time.time() - box.timeout >= box.created ) 
            or (common.mouse_clicked and common.inrange(common.mouse_pos[0], 0, box.size_x) and common.inrange(common.mouse_pos[1], mb_y, mb_y + box.size_y))):
            common.MBs.remove(box)
        mb_y += box.size_y+1
    
    for button in common.active_buttons:
        if (common.mouse_clicked 
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
    

def main_menu_update():
    global UDP, open_hosts_update_task
    
    if (game.last_gamestate != game.gamestate):
        quit_button = common.ButtonInteractive(
            text = "Quit",
            position=(0,0),
            callback = task.JoinedTask(
                [
                    task.BasicTask(eventhandler.EventHandler.quit),
                    # task.BasicTask(print, "Quit"),
                    task.BasicTask(common.STOP),
                ]
            )
        )
        quit_button_x = common.WIN_X - quit_button.size_x - 10
        quit_button_y = common.WIN_Y - quit_button.size_y - 10
        quit_button.position = (quit_button_x, quit_button_y)
        common.active_buttons.append(quit_button)
        
    
    if UDP==None:
        UDP = connection.UDP_Sock(connection.ALL_INTERFACES, connection.UDP_BROADCAST_PORT)
        common.LOG("UDP socket opened")
    if (not open_hosts_update_task):
        open_hosts_update_task = task.ThreadTask(open_hosts_update_func)
        open_hosts_update_task()
        common.LOG("open hosts update thread launched")
    if (not UDP.runningflag):
        UDP.start_sending(common.json.dumps({"name": "myname", "play": "ready"}), timestep=5)
        common.LOG("Broadcast started")
        
                

def preparing_menu_update():
    pass

def game_menu_update():
    pass

def game_update():
    if (game.last_gamestate != game.gamestate):
        common.active_buttons.clear()
    
    all_update()
    match game.gamestate:
        case common.GameState.MAIN_MENU:
            main_menu_update()
        
        case common.GameState.PREPARING_MENU:
            pass
        
        case common.GameState.GAME_MENU:
            pass
    game.last_gamestate = game.gamestate
        
