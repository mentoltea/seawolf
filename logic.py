import typing
import json
import time

import eventhandler
from eventhandler import messages
from messages import prelogic
from prelogic import ui
from prelogic import game
from prelogic import common
from prelogic import connection 
from prelogic import task

# import prelogic
# import common
# import connection
# import eventhandler
# import game
# import tasks.task as task

def open_UDP_socket():
    if prelogic.UDP==None:
        prelogic.UDP = connection.UDP_Sock(connection.ALL_INTERFACES, connection.UDP_BROADCAST_PORT)
        prelogic.LOG("UDP socket opened")

def successfull_connection(username: str, addr: tuple[str,str]):
    print("succes")
    ui.dialogs.append(
        ui.Dialog(
            text="Succesfully connected!",
            button_left=ui.ButtonInteractive(
                text="Close connection",
                position=(0,0),
                callback=task.BasicTask(reject_connection, username, addr)
            )
        )
    )

def connect_to(username: str, addr: tuple[str,str], port: str):
    try:
        prelogic.TCP = connection.TCP_Sock(addr[0], port, is_server=False)
        prelogic.TCP.send("Success client")
        successfull_connection(username, addr)
    except Exception as e:
        prelogic.ERROR(str(e))
        reject_connection(username, addr)

def wait_connection(username: str, addr: tuple[str,str], sleeptime: float, timestep: float = 0.5):
    elapsed: float = 0
    while (elapsed < sleeptime):
        time.sleep(timestep)
        elapsed += timestep
        if (not prelogic.TCP):
            break
        if (prelogic.TCP.connected):
            print(str(prelogic.TCP.recv(0.5)))
            successfull_connection(username, addr)
        
    if (not prelogic.TCP or not prelogic.TCP.connected):
        reject_connection(username, addr)

def accept_connection(username: str, addr: tuple[str,str]):
    tcp_port = connection.TCP_PORT
    prelogic.TCP = connection.TCP_Sock(connection.ALL_INTERFACES, str(tcp_port), is_server=True)
    accept_task = task.ThreadTask(prelogic.TCP.accept)
    accept_task()
    connection.EXPECTED_HOSTS.append(addr[0])
    if (prelogic.UDP):
        prelogic.UDP.send(messages.accept_connection_message(tcp_port), addr[0], int(addr[1]))
    wait_task = task.ThreadTask(wait_connection, username, addr, 5)
    wait_task()

def rejected_connection(username: str, addr: tuple[str,str]):
    if (prelogic.TCP):
        prelogic.TCP.stop()
        prelogic.TCP = None
    if (addr[0] in prelogic.sent_requests): 
        prelogic.sent_requests.remove(addr[0])
    if (addr[0] in connection.EXPECTED_HOSTS):
        connection.EXPECTED_HOSTS.remove(addr[0])
    prelogic.LOG(f"Rejection from {username}:{addr[0]}")

def reject_connection(username: str, addr: tuple[str,str]):
    if (prelogic.TCP):
        prelogic.TCP.stop()
        prelogic.TCP = None
    if (prelogic.UDP):
        prelogic.UDP.send(messages.reject_connection_message(), addr[0], int(addr[1]))
    if (addr[0] in prelogic.sent_requests): 
        prelogic.sent_requests.remove(addr[0])
    if (addr[0] in connection.EXPECTED_HOSTS): 
        connection.EXPECTED_HOSTS.remove(addr[0])
        prelogic.LOG(f"Request from {username}:{addr[0]} rejected")

def wait_for_reply_or_deny(ip: str, sleeptime: float=5):
    time.sleep(sleeptime)
    if (prelogic.TCP == None or prelogic.TCP.host != ip):
        connection.EXPECTED_HOSTS.remove(ip)

def host_is_choosen(username: str, addr: tuple[str,str]):
    if (addr[0] in connection.EXPECTED_HOSTS or addr[0] in prelogic.sent_requests):
        return
    print(username, addr)
    if (prelogic.UDP):
        prelogic.UDP.send(messages.request_connection_message(), addr[0], int(addr[1]))
        prelogic.sent_requests.append(addr[0])
    prelogic.LOG(f"Request sent to {addr[0]}")

def open_hosts_clear():
    prelogic.open_hosts.clear()
    prelogic.open_hosts_buttons.clear()

def open_hosts_update_func():
    open_hosts_clear()
    while (prelogic.game.gamestate == prelogic.common.GameState.MAIN_MENU and prelogic.UDP!=None):
        rcv = prelogic.UDP.recv(2)
        # if (prelogic.game.gamestate != prelogic.common.GameState.MAIN_MENU): break
        if (rcv):
            (data, addr) = rcv
            if (addr[0] in prelogic.MYADRRESS):
                continue
            
            jsondata: dict[str, typing.Any] = json.loads(data)
            if (not messages.check_udp_message_validation(jsondata, addr)):
                continue
            
            add: dict[str, typing.Any] = jsondata["add"]
            username: str = add["name"]
                
            match(jsondata["type"]): # type: ignore
                case common.MessageType.BROADCAST:  
                    if (addr[0] in prelogic.open_hosts):
                        continue
                    new_btn = ui.ButtonInteractive(
                            text= f"{username} : {addr[0]}",
                            position= (0,0),
                            callback= task.BasicTask(
                                host_is_choosen,
                                username,
                                addr
                            ),
                            oneclick=False,
                            add=(username, addr),
                            
                            backcolor= (230, 230, 200)
                        )
                    new_btn.size_x = 350
                    new_btn.size_y = 30
                    prelogic.open_hosts_buttons.append(new_btn)
                    prelogic.open_hosts_buttons.sort(key=lambda b: b.add[0])
                    
                    prelogic.open_hosts.append(addr[0])
                    
                    # prelogic.LOG(addr[0] + ": " + common.json.dumps(add))
                
                case common.MessageType.REQUEST_CONN:
                    ui.dialogs.append(ui.Dialog(
                            text=f"Accept play request from {username}:{addr[0]}?",
                            button_left=ui.ButtonInteractive("Accept", 
                                                             (0,0), 
                                                             callback=task.BasicTask(accept_connection, username, addr), 
                                                             oneclick=True),
                            button_right=ui.ButtonInteractive("Reject", 
                                                             (0,0), 
                                                             callback=task.BasicTask(reject_connection, username, addr), 
                                                             oneclick=True),
                            on_timeout_call=task.BasicTask(reject_connection, username, addr),
                            timeout=5
                        )
                    )
                
                case common.MessageType.ANSWER_CONN:
                    try:
                        conn_info: dict[str, typing.Any] = jsondata["connection"]
                        status: bool = conn_info["status"]
                        if (status):
                            port:str = conn_info["port"]
                            conn_task = task.ThreadTask(connect_to, username, addr, port)
                            conn_task()
                        else:
                            rejected_connection(username, addr)
                    except Exception as e:
                        prelogic.ERROR(str(e))
            
    # prelogic.open_hosts_update_task = None

def validate_page():
    if (prelogic.open_hosts_page<0):
        prelogic.open_hosts_page=0
        prelogic.INFO("Negative pages are out of range")
        return
    
    maxpage = open_host_maxpage() #len(open_hosts_buttons) // (open_hosts_onepage + 1)
    
    if (prelogic.open_hosts_page > maxpage):
        prelogic.open_hosts_page=maxpage
        prelogic.INFO("Page is out of range")
        return
    

def open_host_maxpage() -> int:
    N = len(prelogic.open_hosts_buttons)
    if (N==0): return 0
    return (N-1)//prelogic.open_hosts_onepage

def open_hosts_page_add(num: int):
    prelogic.open_hosts_page += num
    validate_page()


def all_update():
    if (ui.active_dialog == None and len(ui.dialogs)>0):
        ui.active_dialog = ui.dialogs.pop(0)
        
    if (ui.active_dialog):
        if (common.mouse_clicked 
            and common.mouse_button == 1):
            ui.active_dialog.click_check(common.mouse_pos[0], common.mouse_pos[1])
            common.mouse_clicked = False
            
        if (time.time() - ui.active_dialog.created_at >= ui.active_dialog.timeout):
            ui.active_dialog = None
    
    mb_y = 0
    for box in ui.MBs:
        if ((time.time() - box.created >=  box.timeout) 
            or (common.mouse_clicked and common.mouse_button == 1 and common.inrange(common.mouse_pos[0], 0, box.size_x) and common.inrange(common.mouse_pos[1], mb_y, mb_y + box.size_y))):
            ui.MBs.remove(box)
        mb_y += box.size_y+1
    
    for button in ui.active_buttons:
        if (common.mouse_clicked 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
            
        
def main_menu_init():
    if (prelogic.TCP):
        prelogic.TCP.stop()
        prelogic.TCP = None
    
    common.change_window_size((1280, 720))
    # ui.dialogs.append(
    #     ui.Dialog(
    #         text= "It is main menu!",
    #         button_left= ui.ButtonInteractive(
    #             text= "Close",
    #             position=(0,0),
    #             callback= None
    #         ),
    #         # button_right= common.ButtonInteractive(
    #         #     text= "Not close",
    #         #     position=(0,0),
    #         #     callback= None
    #         # ),
    #         timeout=5
    #     )
    # )
    
    
    quit_button = ui.ButtonInteractive(
        text = "Quit",
        position=(0,0),
        callback = task.JoinedTask(
            [
                task.BasicTask(eventhandler.EventHandler.quit),
                task.BasicTask(common.STOP),
            ]
        )
    )
    quit_button_x = 10
    quit_button_y = common.WIN_Y - quit_button.size_y - 10
    quit_button.position = (quit_button_x, quit_button_y)
    ui.active_buttons.append(quit_button)
    
    clear_hosts_button = ui.ButtonInteractive(
        text = "Clear / Update",
        position=(0,0),
        callback = open_hosts_clear,
        center=True
    )
    
    clear_hosts_button.position = (common.WIN_X - 400 - 50 - clear_hosts_button.size_x,
                                    common.WIN_Y - 10 - clear_hosts_button.size_y)
    ui.active_buttons.append(clear_hosts_button)
    
    
    # ohpnb = open_hosts_page_next_button = common.ButtonInteractive(
    ohpnb = ui.ButtonInteractive(
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
    ui.active_buttons.append(ohpnb)

    # ohppb = open_hosts_page_prev_button = common.ButtonInteractive(
    ohppb = ui.ButtonInteractive(
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
    ui.active_buttons.append(ohppb)
    
    prelogic.open_hosts_page_label = ui.Label(
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

    open_UDP_socket()
    if (not prelogic.open_hosts_update_task):
        prelogic.open_hosts_update_task = task.ThreadTask(open_hosts_update_func)
        prelogic.open_hosts_update_task()
        # prelogic.LOG("open hosts update thread launched")

def main_menu_update():
    if (prelogic.UDP != None):
        if (not prelogic.UDP.runningflag):
            prelogic.UDP.start_sending(
                messages.broadcast_message(),
                timestep=2
            )
            prelogic.LOG("Broadcast started")
    padx = 50
    pady = 10
    cury = 0
    
    validate_page()
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
            
def main_menu_deinit():
    prelogic.open_hosts_page_label = None
    if prelogic.UDP!=None:
        prelogic.UDP.stop()
        # prelogic.UDP = None
    if (prelogic.open_hosts_update_task != None):
        prelogic.open_hosts_update_task = None
    

def preparing_menu_init():
    common.change_window_size((900,400))
    def lcl():
        game.gamestate = common.GameState.MAIN_MENU
    ui.dialogs.append(
        ui.Dialog(
            text= "It is prepare menu!",
            button_left= ui.ButtonInteractive(
                text= "Return back",
                position=(0,0),
                callback= task.BasicTask(
                    lcl
                )
            ),
            # button_right= common.ButtonInteractive(
            #     text= "Not close",
            #     position=(0,0),
            #     callback= None
            # ),
            # timeout=5
        )
    )
def preparing_menu_update():
    pass
def preparing_menu_deinit():
    pass

def game_menu_init():
    pass
def game_menu_update():
    pass
def game_menu_deinit():
    pass

def game_update():
    all_update()
    if (game.last_gamestate != game.gamestate):
        ui.active_buttons.clear()
        ui.active_labels.clear()
        if (game.last_gamestate!=None): prelogic.LOG(game.last_gamestate + " DEINIT")
        match game.last_gamestate:
            case common.GameState.MAIN_MENU:
                main_menu_deinit()
            case common.GameState.PREPARING_MENU:
                preparing_menu_deinit()
            case common.GameState.GAME_MENU:
                game_menu_deinit()
            case _:
                pass
        prelogic.LOG(game.gamestate + " INIT")
        match game.gamestate:
            case common.GameState.MAIN_MENU:
                main_menu_init()
            case common.GameState.PREPARING_MENU:
                preparing_menu_init()
            case common.GameState.GAME_MENU:
                game_menu_init()
            case _:
                pass
        game.last_gamestate = game.gamestate
    match game.gamestate:
        case common.GameState.MAIN_MENU:
            main_menu_update()
        
        case common.GameState.PREPARING_MENU:
            preparing_menu_update()
        
        case common.GameState.GAME_MENU:
            game_menu_update()
        
        case _:
            pass
        
