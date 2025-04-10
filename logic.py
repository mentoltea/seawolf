import common
# from common import *
import tasks.task as task
import game
# from game import *
import connection
# from connection import *
import eventhandler
import typing
# from eventhandler import *


MYUSERNAME = connection.LOCAL_INFO[0]
MYADRRESS = [ip for ip in connection.LOCAL_INFO[2] if not ip.startswith("127.")]

print(MYADRRESS, MYUSERNAME)

UDP: connection.UDP_Sock = None

open_hosts: list[str] = [] #adresses
open_hosts_buttons: list[common.ButtonInteractive] = []
open_hosts_page_label: common.Label = None
open_hosts_page = 0
open_hosts_onepage = 5
open_hosts_update_task: task.ThreadTask = None
open_hosts_selfhost_label = None

def host_is_choosen(username, addr):
    print(f"Choosen host {username} :: {addr[0]}:{addr[1]}")

def open_hosts_clear():
    open_hosts.clear()
    open_hosts_buttons.clear()
    # print("cleared")

def open_hosts_update_func():
    global open_hosts_update_task
    open_hosts_clear()
    while (game.gamestate == common.GameState.MAIN_MENU and UDP!=None):
        rcv = UDP.recv(2)
        if (rcv):
            (data, addr) = rcv
            if (addr[0] in open_hosts or addr[0] in MYADRRESS):
                continue
            jsondata: map[str, typing.Any] = common.json.loads(data)
            if ("type" in jsondata 
                and isinstance(jsondata["type"], str) 
                and jsondata["type"] == common.MessageType.BROADCAST):
                try:
                    add = jsondata["add"]
                    if add["game"] != "seawolf":
                        common.LOG(addr[0] + ": " + "Different game")
                        continue
                    if add["version"] != common.VERSION:
                        common.LOG(addr[0] + ": " + f"Different versions - {common.VERSION} and {add["version"]}")
                        continue
                    username = add["name"]
                    username = username[0:16]
                    if not isinstance(username, str):
                        common.LOG(addr[0] + ": " + f"Invalid name")
                        continue
                    
                    
                    new_btn = common.ButtonInteractive(
                            text= f"{username} : {addr[0]}",
                            position= (0,0),
                            callback= None,
                            oneclick=False,
                            add=(username, addr),
                            
                            backcolor= (230, 230, 200)
                        )
                    new_btn.size_x = 350
                    new_btn.size_y = 30
                    open_hosts_buttons.append(new_btn)
                    open_hosts_buttons.sort(key=lambda b: b.add[0])
                    
                    open_hosts.append(addr[0])
                    
                    common.LOG(addr[0] + ": " + common.json.dumps(add))
                except Exception as e:
                    common.LOG(addr[0] + ": " + "Invalid json file structure")
    open_hosts_update_task = None

def validate_page():
    global open_hosts_page, open_hosts_onepage
    if (open_hosts_page<0):
        open_hosts_page=0
        common.INFO("Negative pages are out of range")
        return
    
    maxpage = open_host_maxpage() #len(open_hosts_buttons) // (open_hosts_onepage + 1)
    
    if (open_hosts_page > maxpage):
        open_hosts_page=maxpage
        common.INFO("Page is out of range")
        return
    

def open_host_maxpage() -> int:
    N = len(open_hosts_buttons)
    if (N==0): return 0
    return (N-1)//open_hosts_onepage

def open_hosts_page_add(num: int):
    global open_hosts_page
    open_hosts_page += num
    validate_page()


def all_update():
    mb_y = 0
    for box in common.MBs:
        if ((common.time.time() - box.timeout >= box.created ) 
            or (common.mouse_clicked and common.mouse_button == 1 and common.inrange(common.mouse_pos[0], 0, box.size_x) and common.inrange(common.mouse_pos[1], mb_y, mb_y + box.size_y))):
            common.MBs.remove(box)
        mb_y += box.size_y+1
    
    for button in common.active_buttons:
        if (common.mouse_clicked 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
    

def main_menu_update():
    global UDP, open_hosts_update_task, open_hosts_page_label
    
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
        quit_button_x = 10
        quit_button_y = common.WIN_Y - quit_button.size_y - 10
        quit_button.position = (quit_button_x, quit_button_y)
        common.active_buttons.append(quit_button)
        
        clear_hosts_button = common.ButtonInteractive(
            text = "Clear / Update",
            position=(0,0),
            callback = open_hosts_clear,
            center=True
        )
        
        clear_hosts_button.position = (common.WIN_X - 400 - 50 - clear_hosts_button.size_x,
                                       common.WIN_Y - 10 - clear_hosts_button.size_y)
        common.active_buttons.append(clear_hosts_button)
        
        
        ohpnb = open_hosts_page_next_button = common.ButtonInteractive(
            text = " > ",
            position=(0,0),
            callback = task.BasicTask(
                open_hosts_page_add,
                1
            ),
            center=True
        )
        ohpnb.position = (
            clear_hosts_button.position[0] + clear_hosts_button.size_x - ohpnb.size_x,
            clear_hosts_button.position[1] - ohpnb.size_y - 10,
        )
        common.active_buttons.append(ohpnb)

        ohppb = open_hosts_page_prev_button = common.ButtonInteractive(
            text = " < ",
            position=(0,0),
            callback = task.BasicTask(
                open_hosts_page_add,
                -1
            ),
            center=True
        )
        ohppb.position = (
            clear_hosts_button.position[0],
            clear_hosts_button.position[1] - ohpnb.size_y - 10,
        )
        common.active_buttons.append(ohppb)
        
        open_hosts_page_label = common.Label(
            text="0/0",
            position=(0,0),
            center=True
        )
        open_hosts_page_label.size_x = clear_hosts_button.size_x - ohpnb.size_x - ohppb.size_x - 2*5
        open_hosts_page_label.size_y = ohppb.size_y
        
        open_hosts_page_label.position = (
            ohppb.position[0] + ohppb.size_x + 5,
            ohppb.position[1],    
        )
        
    
    if UDP==None:
        UDP = connection.UDP_Sock(connection.ALL_INTERFACES, connection.UDP_BROADCAST_PORT)
        common.LOG("UDP socket opened")
    if (not open_hosts_update_task):
        open_hosts_update_task = task.ThreadTask(open_hosts_update_func)
        open_hosts_update_task()
        common.LOG("open hosts update thread launched")
        
    if (not UDP.runningflag):
        UDP.start_sending(
            common.json.dumps(
                {
                    "type" : common.MessageType.BROADCAST,
                    "add" : {
                        "game" : "seawolf",
                        "version" : common.VERSION,
                        "name" : ""#MYUSERNAME
                    }
                }
            ),
            timestep=2
        )
        common.LOG("Broadcast started")
    
    padx = 50
    pady = 10
    cury = 0
    
    validate_page()
    # print(len(open_hosts_buttons))
    maxpage = open_host_maxpage() #len(open_hosts_buttons) // (open_hosts_onepage + 1)
    open_hosts_page_label.set_text(f"{open_hosts_page+1}/{maxpage+1}")
    
    for i in range(0, open_hosts_onepage):
        idx = open_hosts_page*open_hosts_onepage + i
        if (idx >= len(open_hosts_buttons)): break
        
        button = open_hosts_buttons[idx]
        button.position = (common.WIN_X - padx - button.size_x,
                           common.WIN_Y - pady - button.size_y - cury)
        cury += button.size_y + pady
        
        if (common.mouse_clicked 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
            host_is_choosen(*button.add)
            
                

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
            preparing_menu_update()
        
        case common.GameState.GAME_MENU:
            game_menu_update()
            
    game.last_gamestate = game.gamestate
        
