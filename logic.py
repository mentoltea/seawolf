from common import *
from game import *
from connection import *
from eventhandler import *

UDP: UDP_Sock = None

open_hosts: list[tuple[str, str]] = []

open_hosts_update_task: task.ThreadTask = None

def open_hosts_update_func():
    while (gamestate == GameState.MAIN_MENU and UDP!=None):
        rcv = UDP.recv(1)
        if (rcv):
            (data, addr) = rcv
            jsondata = json.loads(data)
            LOG(json.dumps(jsondata))
    open_hosts_update_task = None


def all_update():
    # print(len(MBs))
    for box in MBs:
        if (time.time() - box.created >= box.timeout):
                MBs.remove(box)

def main_menu_update():
    global UDP, open_hosts_update_task
    if UDP==None:
        UDP = UDP_Sock(ALL_INTERFACES, UDP_BROADCAST_PORT)
        LOG("UDP socket opened")
    if (not open_hosts_update_task):
        open_hosts_update_task = task.ThreadTask(open_hosts_update_func)
        open_hosts_update_task()
        LOG("open hosts update thread launched")
    if (not UDP.runningflag):
        UDP.start_sending(json.dumps({"name": "myname", "play": "ready"}))
        LOG("Broadcast started")
        
                

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
        
