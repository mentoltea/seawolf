import typing
import json
import time

import messages

prelogic = messages.prelogic
common = prelogic.common
connection = prelogic.connection
eventhandler = prelogic.eventhandler
game = prelogic.game
task = prelogic.task

# import prelogic
# import common
# import connection
# import eventhandler
# import game
# import tasks.task as task

def host_is_choosen(username, addr):
    print(username, addr)
    # pass

def open_hosts_clear():
    prelogic.open_hosts.clear()
    prelogic.open_hosts_buttons.clear()
    # print("cleared")

def open_hosts_update_func():
    open_hosts_clear()
    while (prelogic.game.gamestate == prelogic.common.GameState.MAIN_MENU and prelogic.UDP!=None):
        rcv = prelogic.UDP.recv(2)
        if (rcv):
            (data, addr) = rcv
            if (addr[0] in prelogic.open_hosts or addr[0] in prelogic.MYADRRESS):
                continue
            
            jsondata: map[str, typing.Any] = json.loads(data)
            if (not messages.check_udp_message_validation(jsondata, addr)):
                continue
                
            match(jsondata["type"]):
                case common.MessageType.BROADCAST:  
                    add = jsondata["add"]
                    username = add["name"]
                    
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
                    prelogic.open_hosts_buttons.append(new_btn)
                    prelogic.open_hosts_buttons.sort(key=lambda b: b.add[0])
                    
                    prelogic.open_hosts.append(addr[0])
                    
                    common.LOG(addr[0] + ": " + common.json.dumps(add))
                
                case common.MessageType.REQUEST_CONN:
                    eventhandler.EventHandler.connection_requested(username=username,
                                                                   addr=addr)
            
    prelogic.open_hosts_update_task = None

def validate_page():
    if (prelogic.open_hosts_page<0):
        prelogic.open_hosts_page=0
        common.INFO("Negative pages are out of range")
        return
    
    maxpage = open_host_maxpage() #len(open_hosts_buttons) // (open_hosts_onepage + 1)
    
    if (prelogic.open_hosts_page > maxpage):
        prelogic.open_hosts_page=maxpage
        common.INFO("Page is out of range")
        return
    

def open_host_maxpage() -> int:
    N = len(prelogic.open_hosts_buttons)
    if (N==0): return 0
    return (N-1)//prelogic.open_hosts_onepage

def open_hosts_page_add(num: int):
    prelogic.open_hosts_page += num
    validate_page()


def all_update():
    # print(common.active_dialog)
    if (common.active_dialog == None and len(common.dialogs)>0):
        common.active_dialog = common.dialogs.pop(0)
    
    mb_y = 0
    for box in common.MBs:
        if ((time.time() - box.created >=  box.timeout) 
            or (common.mouse_clicked and common.mouse_button == 1 and common.inrange(common.mouse_pos[0], 0, box.size_x) and common.inrange(common.mouse_pos[1], mb_y, mb_y + box.size_y))):
            common.MBs.remove(box)
        mb_y += box.size_y+1
    
    for button in common.active_buttons:
        if (common.mouse_clicked 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
    
    if (common.active_dialog):
        if (common.mouse_clicked 
            and common.mouse_button == 1):
            common.active_dialog.click_check(common.mouse_pos[0], common.mouse_pos[1])
            
        # print(common.active_dialog.timeout)
        if (time.time() - common.active_dialog.created_at >= common.active_dialog.timeout):
            common.active_dialog = None
            
        
    

def main_menu_update():
    
    if (game.last_gamestate != game.gamestate):
        common.dialogs.append(
            common.Dialog(
                text= "It is main menu!",
                button_left= common.ButtonInteractive(
                    text= "Close",
                    position=(0,0),
                    callback= None
                ),
                button_right= common.ButtonInteractive(
                    text= "Not close",
                    position=(0,0),
                    callback= None
                ),
                timeout=5
            )
        )
        
        
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
        
        prelogic.open_hosts_page_label = common.Label(
            text="0/0",
            position=(0,0),
            center=True
        )
        prelogic.open_hosts_page_label.size_x = clear_hosts_button.size_x - ohpnb.size_x - ohppb.size_x - 2*5
        prelogic.open_hosts_page_label.size_y = ohppb.size_y
        
        prelogic.open_hosts_page_label.position = (
            ohppb.position[0] + ohppb.size_x + 5,
            ohppb.position[1],    
        )
        
    
    if prelogic.UDP==None:
        prelogic.UDP = connection.UDP_Sock(connection.ALL_INTERFACES, connection.UDP_BROADCAST_PORT)
        common.LOG("UDP socket opened")
    if (not prelogic.open_hosts_update_task):
        prelogic.open_hosts_update_task = task.ThreadTask(open_hosts_update_func)
        prelogic.open_hosts_update_task()
        common.LOG("open hosts update thread launched")
        
    if (not prelogic.UDP.runningflag):
        prelogic.UDP.start_sending(
            messages.broadcast_message(),
            timestep=2
        )
        common.LOG("Broadcast started")
    
    padx = 50
    pady = 10
    cury = 0
    
    validate_page()
    # print(len(open_hosts_buttons))
    maxpage = open_host_maxpage() #len(open_hosts_buttons) // (open_hosts_onepage + 1)
    if (prelogic.open_hosts_page_label):
        prelogic.open_hosts_page_label.set_text(f"{prelogic.open_hosts_page+1}/{maxpage+1}")
    
    for i in range(0, prelogic.open_hosts_onepage):
        idx = prelogic.open_hosts_page*prelogic.open_hosts_onepage + i
        if (idx >= len(prelogic.open_hosts_buttons)): break
        
        button = prelogic.open_hosts_buttons[idx]
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
        
