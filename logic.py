import typing
import json
import time
import random
import eventhandler # type: ignore
from eventhandler import bot
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

# def check_connection_alive(username: str, addr: tuple[str,str], interval: float = 1):
#     if (prelogic.TCP == None): 
#         rejected_connection(username, addr)
#         return
    
#     shift = False
#     if (prelogic.TCP.is_server):
#         shift = True
#     while (prelogic.TCP != None and prelogic.TCP.connected): # type: ignore
#         # _ = prelogic.TCP.recv(1) 
#         if (shift):
#             prelogic.TCP.send(messages.check_conn_message())
#             data = prelogic.TCP.recv(3*interval)
#             if (not messages.approve_conn_message_check(data)):
#                 break
#             
#         else:
#             data = prelogic.TCP.recv(3*interval)
#             if (messages.check_conn_message_check(data)):
#                 prelogic.TCP.send(messages.approve_conn_message())
#             else:
#                 break
#             
        
#         shift = not shift
#         # if connection was closed, 
#         # ConnectionError will raise and be catched inside TCP,
#         # calling TCP.close() and setting TCP.connected = False
#         time.sleep(interval) 
#     rejected_connection(username, addr)
    

def open_UDP_socket():
    if prelogic.UDP==None:
        prelogic.UDP = connection.UDP_Sock(connection.ALL_INTERFACES, connection.UDP_BROADCAST_PORT)
        prelogic.LOG("UDP socket opened")

def successfull_connection(username: str, addr: tuple[str,str]):
    if (prelogic.TCP): print(prelogic.TCP.recv(2))
    # check_conn_task = task.ThreadTask(check_connection_alive, username, addr)
    # check_conn_task()
    eventhandler.ActiveConnection = prelogic.TCP
    
    # game.gamestate = common.GameState.PREPARING_MENU
    game.set_gamestate(common.GameState.PREPARING_MENU)

def connect_to(username: str, addr: tuple[str,str], port: str):
    try:
        prelogic.TCP = connection.TCP_Sock(addr[0], port, is_server=False)
        # prelogic.TCP.send("Success from client")
        eventhandler.safesend(prelogic.TCP, "Success from client")
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
            # prelogic.TCP.send("Success from server")
            eventhandler.safesend(prelogic.TCP, "Success from server")
            successfull_connection(username, addr)
            return
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
    # game.gamestate = common.GameState.MAIN_MENU
    game.set_gamestate(prelogic.return_state)
    if (prelogic.TCP):
        prelogic.TCP.stop()
        prelogic.TCP = None
    if (addr[0] in prelogic.sent_requests): 
        prelogic.sent_requests.remove(addr[0])
    if (addr[0] in connection.EXPECTED_HOSTS):
        connection.EXPECTED_HOSTS.remove(addr[0])
    prelogic.LOG(f"Rejection from {username}:{addr[0]}")

def reject_connection(username: str, addr: tuple[str,str]):
    # game.gamestate = common.GameState.MAIN_MENU
    game.set_gamestate(prelogic.return_state)
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

def wait_for_reply_or_forget(username: str, addr: tuple[str,str], sleeptime: float=5):
    time.sleep(sleeptime)
    if (prelogic.TCP == None or prelogic.TCP.host != addr[0]):
        if (addr[0] in prelogic.sent_requests): prelogic.sent_requests.remove(addr[0])

def host_is_choosen(username: str, addr: tuple[str,str]):
    if (addr[0] in connection.EXPECTED_HOSTS or addr[0] in prelogic.sent_requests):
        return
    print(username, addr)
    if (prelogic.UDP):
        prelogic.UDP.send(messages.request_connection_message(), addr[0], int(addr[1]))
        prelogic.sent_requests.append(addr[0])
        wait_task = task.ThreadTask(wait_for_reply_or_forget, username, addr)
        wait_task()
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
            
            try:
                jsondata: dict[str, typing.Any] = json.loads(data)
                if (not messages.check_udp_message_validation(jsondata, addr)):
                    continue
            except Exception as e:
                prelogic.ERROR(str(e))
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
        if (common.mouse_button_up 
            and common.mouse_button == 1):
            ui.active_dialog.click_check(common.mouse_pos[0], common.mouse_pos[1])
            common.mouse_button_up = False
        if (ui.active_dialog.close):
            ui.active_dialog = None
        elif (time.time() - ui.active_dialog.created_at >= ui.active_dialog.timeout):
            ui.active_dialog.on_timeout = True
            ui.active_dialog = None
    
    mb_y = 0
    for box in ui.MBs:
        if ((time.time() - box.created >=  box.timeout) 
            or (common.mouse_button_up and common.mouse_button == 1 and common.inrange(common.mouse_pos[0], 0, box.size_x) and common.inrange(common.mouse_pos[1], mb_y, mb_y + box.size_y))):
            ui.MBs.remove(box)
        mb_y += box.size_y+1
    
    for button in ui.active_buttons:
        if (common.mouse_button_up 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y)):
            button.avtivate()
            
            
        
def main_menu_init():
    if (eventhandler.ActiveConnection):
        eventhandler.ActiveConnection.stop()
        eventhandler.ActiveConnection = None
    
    if (prelogic.TCP):
        prelogic.TCP.stop()
        prelogic.TCP = None
    
    connection.EXPECTED_HOSTS.clear()
    prelogic.sent_requests.clear()
    
    common.change_window_size((720, 180))
    
    prelogic.return_state = common.GameState.MAIN_MENU
    
    my_name_label = ui.Label(
        text=f"My name: {prelogic.MYUSERNAME}",
        position=(0,0),
        font=ui.Font22,
        center=False,
        backcolor=(220,220,250)
    )
    
    quit_button = ui.ButtonInteractive(
        text = "Return back",
        position=(0,0),
        callback = task.BasicTask(game.set_gamestate, common.GameState.CHOOSE_MODE_MENU),
        font=ui.Font22
    )
    quit_button_x = 10
    quit_button_y = common.WIN_Y - quit_button.size_y - 10
    quit_button.position = (quit_button_x, quit_button_y)
    ui.active_buttons.append(quit_button)
    
    clear_hosts_button = ui.ButtonInteractive(
        text = "Clear / Update",
        position=(0,0),
        callback = open_hosts_clear,
        center=True,
        font=ui.Font22
    )
    
    # clear_hosts_button.position = (common.WIN_X - 400 - 50 - clear_hosts_button.size_x,
    #                                 common.WIN_Y - 10 - clear_hosts_button.size_y)
    clear_hosts_button.position = (quit_button_x + my_name_label.size_x - clear_hosts_button.size_x,
                                    quit_button_y + quit_button.size_y - clear_hosts_button.size_y)
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
        center=True,
        font=ui.Font22
    )
    prelogic.open_hosts_page_label.size_x = clear_hosts_button.size_x - ohpnb.size_x - ohppb.size_x - 2*5
    prelogic.open_hosts_page_label.size_y = ohppb.size_y
    
    prelogic.open_hosts_page_label.position = (
        ohppb.position[0] + ohppb.size_x + 5,
        ohppb.position[1],    
    )
    
    my_name_label.position = (
        quit_button_x,
        # prelogic.open_hosts_page_label.position[1] - 20 - my_name_label.size_y
        20
    )
    ui.active_labels.append(my_name_label)

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
    padx = 20
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
        
        if (common.mouse_button_up 
            and common.mouse_button == 1
            and common.inrange(common.mouse_pos[0], button.position[0], button.position[0] + button.size_x -1) 
            and common.inrange(common.mouse_pos[1], button.position[1], button.position[1] + button.size_y -1)):
            button.avtivate()
            
def main_menu_deinit():
    prelogic.open_hosts_page_label = None
    if prelogic.UDP!=None:
        prelogic.UDP.stop()
        # prelogic.UDP = None
    if (prelogic.open_hosts_update_task != None):
        prelogic.open_hosts_update_task = None
    
def play_singleplayer():
    server = bool(random.randint(0,1))
    eventhandler.ActiveConnection = bot.Bot_Sock(server)
    game.set_gamestate(common.GameState.PREPARING_MENU)

def choose_mode_menu_init():
    common.change_window_size((300, 200))
    
    prelogic.return_state = common.GameState.CHOOSE_MODE_MENU
    
    singleplayer_button = ui.ButtonInteractive(
        text="Singleplayer",
        position=(0,0),
        callback= task.BasicTask(play_singleplayer),
        font=ui.Font24
    )
    singleplayer_button.position = (common.WIN_X/2 - singleplayer_button.size_x/2,
                                    common.WIN_Y*1/4 - singleplayer_button.size_y/2,)
    ui.active_buttons.append(singleplayer_button)
    
    
    multiplayer_button = ui.ButtonInteractive(
        text="Multiplayer",
        position=(0,0),
        callback= task.BasicTask(game.set_gamestate, common.GameState.MAIN_MENU),
        font=ui.Font24
    )
    multiplayer_button.position = (common.WIN_X/2 - multiplayer_button.size_x/2,
                                    common.WIN_Y*2/4 - multiplayer_button.size_y/2,)
    ui.active_buttons.append(multiplayer_button)
    
    
    quit_button = ui.ButtonInteractive(
        text="Quit",
        position=(0,0),
        callback= common.STOP,
        font=ui.Font24
    )
    quit_button.position = (common.WIN_X/2 - quit_button.size_x/2,
                                    common.WIN_Y*3/4 - quit_button.size_y/2,)
    ui.active_buttons.append(quit_button)
    
    
def choose_mode_menu_update():
    pass
def choose_mode_menu_deinit():
    pass

def connection_check_func(sec_per_check: float = 3):
    while (eventhandler.ActiveConnection != None and eventhandler.ActiveConnection.connected):
        if (time.time() - sec_per_check >= eventhandler.LastCheckedConnection):
            if not eventhandler.safesend(eventhandler.ActiveConnection, messages.check_conn_message()):
                if (not prelogic.looking_game_results): game.set_gamestate(prelogic.return_state)
                return
            if not eventhandler.ActiveConnection.connected:
                if (not prelogic.looking_game_results): game.set_gamestate(prelogic.return_state)
                return
            eventhandler.LastCheckedConnection = time.time()
        time.sleep(sec_per_check)
    if (not prelogic.looking_game_results): game.set_gamestate(prelogic.return_state)

def prep_menu_game_menu_data_recv_func(interval: float = 1):
    while (game.gamestate in [common.GameState.PREPARING_MENU, common.GameState.GAME_MENU]):
        if (eventhandler.ActiveConnection == None or eventhandler.ActiveConnection.connected == False):
            if (not prelogic.looking_game_results): game.set_gamestate(prelogic.return_state)
            return
        
        rcv = eventhandler.ActiveConnection.recv(interval/2)
        if (rcv == None): continue
        
        datas = rcv.decode("utf-8").split(messages.TCP_DELIMITER)
        for data in datas:
            if data == "": continue
            prelogic.LOG(data)
            # data = data.removeprefix(messages.TCP_DELIMITER).removesuffix(messages.TCP_DELIMITER)
            try:
                jsondata = json.loads(data)
                mtype : str = jsondata["type"]
            
                match (mtype):
                    case common.MessageType.CHECK_CONN:
                        eventhandler.LastCheckedConnection = time.time()
                    
                    case common.MessageType.GAME_EVENT:
                        event: dict[str, typing.Any] = jsondata["event"]
                        etype: str = event["type"]
                        match (etype):
                            case common.GameEventType.READY:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if (game.game):
                                    game.game.opponent_ready = True
                                if (prelogic.opponent_ready_label):
                                    prelogic.opponent_ready_label.set_text("Opponent Is Ready")
                                    prelogic.opponent_ready_label.fontcolor = ui.LIGHTGREEN
                            case common.GameEventType.UNREADY:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if (game.game):
                                    game.game.opponent_ready = False
                                if (prelogic.opponent_ready_label):
                                    prelogic.opponent_ready_label.set_text("Opponent Is Not Ready")
                                    prelogic.opponent_ready_label.fontcolor = ui.LIGHTRED
                            
                            case common.GameEventType.ASK_START_GAME:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if (game.game):
                                    
                                    game.game.opponent_ready = True
                                    if (prelogic.opponent_ready_label):
                                        prelogic.opponent_ready_label.set_text("Opponent Is Ready")
                                        prelogic.opponent_ready_label.fontcolor = ui.LIGHTGREEN
                                        
                                    if (game.game.ready):
                                        eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_appr_message())
                                    else:
                                        eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_decl_message())
                            
                            case common.GameEventType.START_GAME_DECLINE:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if (game.game):
                                    game.game.opponent_ready = False
                                if (prelogic.opponent_ready_label):
                                    prelogic.opponent_ready_label.set_text("Opponent Is Not Ready")
                                    prelogic.opponent_ready_label.fontcolor = ui.LIGHTRED
                                # prelogic.INFO("Opponent is not ready yet")
                                
                            case common.GameEventType.START_GAME_APPROVE:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if game.game:
                                    if game.game.ready:
                                        eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_sappr_message())
                                        game.set_gamestate(common.GameState.GAME_MENU)
                                    else:
                                        eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_decl_message())
                            
                            case common.GameEventType.START_GAME_SECOND_APPROVE:
                                if (game.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                if game.game:
                                    if game.game.ready:
                                        game.set_gamestate(common.GameState.GAME_MENU)
                            
                            # ------------------------------------------------------------------
                            
                            case common.GameEventType.SURRENDER_GAME:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                prelogic.looking_game_results = True
                                eventhandler.ActiveConnection.connected = False
                                
                                ui.dialogs.append(
                                    ui.Dialog(
                                        text= "You won - Opponent surrendered",
                                        font=ui.Font36,
                                        button_left= ui.ButtonInteractive(
                                            text= "Go back",
                                            position=(0,0),
                                            callback= task.BasicTask(game.set_gamestate, prelogic.return_state),
                                            font = ui.Font30
                                        )
                                    )
                                )
                            
                            case common.GameEventType.END_GAME:
                                if (game.gamestate != common.GameState.GAME_MENU): continue

                                end_game()
                            
                            # ------------------------------------------------------------------
                            
                            case common.GameEventType.MAKE_MOVE:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if (game.game):
                                    cell = game.game.mymap[iy][ix]
                                    match cell:
                                        case game.CellType.HIDDEN:
                                            eventhandler.safesend( eventhandler.ActiveConnection, messages.move_empty_message(move))
                                            game.set_move_mymap(game.game, game.game.mymap, ix, iy, game.CellType.EMPTY)
                                            prelogic.mymap_light = (ix, iy)
                                            prelogic.mymap_from = time.time()
                                            prelogic.mymap_for = 1
                                            set_turn(0)
                                        
                                        case game.CellType.BOAT:
                                            game.game.mymap[iy][ix] = game.CellType.SHOT
                                            if (game.isKilled(game.game, game.game.mymap, ix, iy)):
                                                eventhandler.safesend( eventhandler.ActiveConnection, messages.move_killed_message(move))
                                                game.set_move_mymap(game.game, game.game.mymap, ix, iy, game.CellType.KILLED)
                                            else:
                                                eventhandler.safesend( eventhandler.ActiveConnection, messages.move_shot_message(move))
                                                game.set_move_mymap(game.game, game.game.mymap, ix, iy, game.CellType.SHOT)
                                            if (check_win() != 0):
                                                end_game()
                                            prelogic.mymap_light = (ix, iy)
                                            prelogic.mymap_from = time.time()
                                            prelogic.mymap_for = 1
                                            set_turn(1)
                                        
                                        case _:
                                            prelogic.LOG(move + " " + str(cell))
                                            eventhandler.safesend( eventhandler.ActiveConnection, messages.bad_move_message(move))
                                    left_labels_update()
                            
                            case common.GameEventType.MOVE_EMPTY:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if game.game:
                                    game.set_move_enemymap(game.game, game.game.enemymap, ix, iy, game.CellType.EMPTY)
                                prelogic.enemymap_light = (ix, iy)
                                prelogic.enemymap_from = time.time()
                                prelogic.enemymap_for = 1
                                set_turn(1)
                                
                            case common.GameEventType.MOVE_SHOT:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if game.game:
                                    game.set_move_enemymap(game.game, game.game.enemymap, ix, iy, game.CellType.SHOT)
                                prelogic.enemymap_light = (ix, iy)
                                prelogic.enemymap_from = time.time()
                                prelogic.enemymap_for = 1
                                set_turn(0)
                            
                            case common.GameEventType.MOVE_KILLED:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if game.game:
                                    game.set_move_enemymap(game.game, game.game.enemymap, ix, iy, game.CellType.KILLED)
                                left_labels_update()
                                if (check_win() != 0):
                                    end_game()
                                prelogic.enemymap_light = (ix, iy)
                                prelogic.enemymap_from = time.time()
                                prelogic.enemymap_for = 1
                                set_turn(0)
                            
                            case common.GameEventType.BAD_MOVE:
                                if (game.gamestate != common.GameState.GAME_MENU): continue
                                
                                prelogic.INFO("Bad move")
                                prelogic.LOG("Bad move")
                                set_turn(0)
                            
                            
                            case _:
                                prelogic.LOG(f"Unknown event type {etype}")
                        
                    
                    case _:
                        prelogic.LOG(f"Unknown message type {mtype}")
                
            except Exception as e:
                prelogic.ERROR(str(e))
                print(data)
                game.set_gamestate(prelogic.return_state)
                return

        time.sleep(interval)

def set_ready(state: bool):
    if (game.game):
        if (state == True):
            for (_, c) in prelogic.current_ships.items():
                if c > 0: return
        
        game.game.ready = state
        
    if (prelogic.ready_button):
        if state:
            prelogic.ready_button.set_text("I Am Ready")
            prelogic.ready_button.fontcolor = ui.VERYLIGHTGREEN
        else:
            prelogic.ready_button.set_text("I Am Not Ready")
            prelogic.ready_button.fontcolor = ui.VERYLIGHTRED
            
    if (eventhandler.ActiveConnection):
        if state:
            eventhandler.safesend(eventhandler.ActiveConnection, messages.ready_message())
        else:
            eventhandler.safesend(eventhandler.ActiveConnection, messages.unready_message())
    
def swicth_ready():
    if (game.game):
        current = game.game.ready
        set_ready(not current)
        if (game.game.ready and game.game.opponent_ready):
            eventhandler.safesend(eventhandler.ActiveConnection, messages.ask_start_game_message())

def place_back_ship():
    if (prelogic.holding_ship):
        btn_other_idx = None
        for i, b in enumerate(prelogic.current_ships_buttons):
            if b.add[1] == prelogic.holding_ship:
                btn_other_idx = i
                break
        if (btn_other_idx == None):
            prelogic.LOG(f"Cannot find button with add val {prelogic.holding_ship}")
        else:
            take_ship(btn_other_idx)

def take_back_ship(l: int):
    btn_other_idx = None
    for i, b in enumerate(prelogic.current_ships_buttons):
        if b.add[1] == l:
            btn_other_idx = i
            break
        
    if (btn_other_idx == None):
        prelogic.LOG(f"Cannot find button with add val {prelogic.holding_ship}")
    else:
        take_ship(btn_other_idx)

def take_ship(btn_idx: int):
    btn = prelogic.current_ships_buttons[btn_idx]
    l: int = btn.add[1]
    cnt = prelogic.current_ships[l]
    if l == prelogic.holding_ship:
        prelogic.current_ships[l] = cnt+1
        prelogic.holding_ship = 0
    elif (cnt>0):
        if (prelogic.holding_ship):
            place_back_ship()
        prelogic.current_ships[l] = cnt-1
        prelogic.holding_ship = l
    btn.set_text(f"{l}-deck: {prelogic.current_ships[l]}")

def place_map_ship() -> bool:
    if (game.game == None):
        return False
    if (prelogic.holding_ship == 0): 
        return False
    (ix, iy) = prelogic.editmap_mouse_ipos
    
    if not game.canPlaceShip(game.game, game.game.editmap, prelogic.holding_ship, ix, iy, prelogic.holding_orientation):
        return False
    
    game.placeShip(game.game, game.game.editmap, prelogic.holding_ship, ix, iy, prelogic.holding_orientation)
    prelogic.holding_ship = 0
    
    return True

def autoplace():
    if (not game.game):
        return
    place_back_ship()
    remaining_ships = sorted(prelogic.current_ships.items(), reverse=True)
    for (l, c) in remaining_ships:
        for _ in range(c):
            tries = 0
            while tries < 20:
                ix = random.randint(0, 9)
                iy = random.randint(0, 9)
                orient = random.randint(0, 1)
                if (game.canPlaceShip(game.game, game.game.editmap, l, ix, iy, orient)):
                    game.placeShip(game.game, game.game.editmap, l, ix, iy, orient)
                    take_back_ship(l)
                    prelogic.holding_ship = 0
                    # prelogic.current_ships[l] -= 1
                    break
                tries += 1

def preparing_menu_init():
    common.change_window_size((850,600))

    game.game = game.GameClass()
    prelogic.looking_game_results = False

    prelogic.current_ships = game.SHIPS_COUNT.copy()
    
    if (eventhandler.ActiveConnection == None):
        # game.gamestate = common.GameState.MAIN_MENU
        game.set_gamestate(prelogic.return_state)
        return
    if eventhandler.ActiveConnection.is_server:
        game.game.turn = 0
    else:
        game.game.turn = 1
        
    conn_check_task = task.ThreadTask(connection_check_func)
    conn_check_task()
    
    data_rcv_task = task.ThreadTask(prep_menu_game_menu_data_recv_func)
    data_rcv_task()
    
    
    prelogic.editmap_pos = (40, 40)
    prelogic.editmap_tilesize = 45
    prelogic.editmap_size = prelogic.editmap_tilesize*10
    
    prelogic.current_ships_buttons.clear()
    prelogic.holding_ship = 0
    curr_ships = sorted(prelogic.current_ships.items())
    for i, (l, c) in enumerate(curr_ships):
        btn = ui.ButtonInteractive(
            text= f"{l}-deck: {c}",\
            position= (0,0),
            callback= task.BasicTask(take_ship, i),
            font=ui.Font30,
            add=(i, l)
        )
        btn.position = (
            prelogic.editmap_pos[0] + prelogic.editmap_size + 20,
            prelogic.editmap_pos[1] + i*(20+btn.size_y)
        )
        prelogic.current_ships_buttons.append(btn)
        ui.active_buttons.append(btn)
        
    return_button = ui.ButtonInteractive(
        text="Return",
        position= (0,0),
        callback= task.BasicTask(game.set_gamestate, prelogic.return_state),
        font=ui.Font30,
        backcolor=(230,230,230)
    )
    return_button.position = (
        prelogic.editmap_pos[0],
        prelogic.editmap_pos[1] + prelogic.editmap_size + 10
    )
    ui.active_buttons.append(return_button)
    
    autoplace_button = ui.ButtonInteractive(
        text="Automatic placement",
        position= (0,0),
        callback= autoplace,
        font=ui.Font30,
        backcolor=(230,230,230)
    )
    autoplace_button.position = (prelogic.editmap_pos[0] + prelogic.editmap_size-autoplace_button.size_x,
                                 prelogic.editmap_pos[1] + prelogic.editmap_size + 10)
    ui.active_buttons.append(autoplace_button)
    
    prelogic.ready_button = ui.ButtonInteractive(
        text="I Am Not Ready",
        position= (0,0),
        callback= swicth_ready,
        font=ui.Font30,
    )
    prelogic.ready_button.position = (
        prelogic.editmap_pos[0] + prelogic.editmap_size + 20,
        autoplace_button.position[1]
    )
    ui.active_buttons.append(prelogic.ready_button)
    
    prelogic.opponent_ready_label = ui.Label(
        text="Opponent Is Not Ready",
        position=(0,0),
        center=True,
        font=ui.Font30
    )
    prelogic.opponent_ready_label.position = (
        prelogic.editmap_pos[0] + prelogic.editmap_size + 20,
        prelogic.ready_button.position[1] - 10 - prelogic.opponent_ready_label.size_y
    )
    
    prelogic.ready_button.position = (
        prelogic.opponent_ready_label.position[0] + (prelogic.opponent_ready_label.size_x - prelogic.ready_button.size_x)/2,
        prelogic.ready_button.position[1]
    )
    ui.active_labels.append(prelogic.opponent_ready_label)
    
    set_ready(False)

def preparing_menu_update():
    prelogic.editmap_mouse_ipos = ((common.mouse_pos[0]-prelogic.editmap_pos[0])//prelogic.editmap_tilesize, 
                                   (common.mouse_pos[1]-prelogic.editmap_pos[1])//prelogic.editmap_tilesize)
    
    if (common.mouse_wheel_down or common.mouse_wheel_up):
        prelogic.holding_orientation = int(not prelogic.holding_orientation)
    
    if (common.mouse_button_down):
        if (prelogic.holding_ship):
            if common.inrange(prelogic.editmap_mouse_ipos[0], 0, 9) and common.inrange(prelogic.editmap_mouse_ipos[1], 0, 9) and common.mouse_button == 1:
                if not place_map_ship():
                    place_back_ship()
            else:
                place_back_ship()
    
        elif common.inrange(prelogic.editmap_mouse_ipos[0], 0, 9) and common.inrange(prelogic.editmap_mouse_ipos[1], 0, 9):
            if (game.game):
                idx = game.selectShipIdx(game.game, game.game.edit_ships, game.game.editmap, prelogic.editmap_mouse_ipos[0], prelogic.editmap_mouse_ipos[1])
                if idx!=-1:
                    (l, (_, _), o) = game.removeShip(game.game, game.game.editmap, idx)
                    prelogic.holding_ship = l
                    prelogic.holding_orientation = o
                    set_ready(False)

        
def preparing_menu_deinit():
    prelogic.ready_button = None
    prelogic.opponent_ready_label = None
    prelogic.current_ships.clear()
    prelogic.current_ships_buttons.clear()

def surrender():
    eventhandler.safesend(eventhandler.ActiveConnection, messages.surrender_game_message())
    game.set_gamestate(prelogic.return_state)

def end_game():
    prelogic.looking_game_results = True
    
    eventhandler.safesend(eventhandler.ActiveConnection, messages.end_game_message())
    if (eventhandler.ActiveConnection): eventhandler.ActiveConnection.connected = False
    
    w = check_win()
    
    text = "Game ended"
    if (w == 1): text = "You won!"
    elif (w==-1): text = "You lost :("
    
    ui.dialogs.append(
        ui.Dialog(
            text= text,
            font=ui.Font36,
            button_left= ui.ButtonInteractive(
                text= "Go back",
                position=(0,0),
                callback= task.BasicTask(game.set_gamestate, prelogic.return_state),
                font = ui.Font30
            )
        )
    )
    
def left_labels_update():
    if (not game.game): return
    en = len(game.game.my_ships) - len(game.game.enemy_ships)
    me = len(game.game.my_ships)
    for s in game.game.my_ships:
        if game.game.mymap[s[1][1]][s[1][0]] == game.CellType.KILLED:
            me -= 1
    
    if (prelogic.my_left_label):
        prelogic.my_left_label.set_text(f"left: {me}")
    if (prelogic.enemy_left_label):
        prelogic.enemy_left_label.set_text(f"left: {en}")
    

# 1 - my win
# -1 - enemy win
# 0 - still playing
def check_win() -> int:
    if (not game.game): return 0
    if (len(game.game.enemy_ships) == len(game.game.my_ships)):
        return 1
    my_killed = 0
    for s in game.game.my_ships:
        if game.game.mymap[s[1][1]][s[1][0]] == game.CellType.KILLED:
            my_killed += 1
    if my_killed == len(game.game.my_ships):
        return -1
    return 0

def set_turn(turn: int):
    if (not prelogic.turn_label): return
    match turn:
        case 0:
            prelogic.turn_label.set_text("My turn")
            prelogic.turn_label.fontcolor = ui.LIGHTGREEN
        case 1:
            prelogic.turn_label.set_text("Enemy turn")
            prelogic.turn_label.fontcolor = ui.LIGHTRED
        case 2:
            prelogic.turn_label.set_text("Wait...")
            prelogic.turn_label.fontcolor = ui.LIGHTGRAY
        case _:
            prelogic.LOG(f"Unknown turn - {turn}")
            turn = 2
            
    if (game.game):
        game.game.turn = turn

def make_move(ix: int, iy: int):
    if (not game.game): return
    if game.game.turn != 0: return
    if (game.game.enemymap[iy][ix] != game.CellType.UNKNOWN):
        prelogic.INFO("Bad move - the cell is already opened")
        return
    
    eventhandler.safesend(eventhandler.ActiveConnection, messages.make_move_message(game.xy2pos(ix, iy)))
    # waiting
    set_turn(2)
        
def game_menu_init():
    common.change_window_size((1080,720))
    if (not eventhandler.ActiveConnection):
        return
    if (not game.game):
        return
    prelogic.looking_game_results = False
    if (game.game):
        game.game.mymap = game.game.editmap.copy()
        game.game.my_ships = game.game.edit_ships.copy()
        
        game.game.enemymap = game.empty_map(game.CellType.UNKNOWN)
        game.game.enemy_ships = []
    
    prelogic.mymap_tilesize = 45
    prelogic.mymap_size = prelogic.mymap_tilesize*10
    prelogic.mymap_mouse_ipos = (0,0)
    
    prelogic.enemymap_tilesize = 45
    prelogic.enemymap_size = prelogic.enemymap_tilesize*10
    prelogic.enemymap_mouse_ipos = (0,0)
    
    my_map_label = ui.Label(
        text="My map:",
        position=(0,0),
        font=ui.Font30
    )
    my_map_label.position = (
        40 + (prelogic.mymap_size - my_map_label.size_x)/2,
        20
    )
    ui.active_labels.append(my_map_label)
    
    enemy_map_label = ui.Label(
        text="Enemy map:",
        position=(0,0),
        font=ui.Font30
    )
    enemy_map_label.position = (
        common.WIN_X - 40 - (enemy_map_label.size_x + prelogic.enemymap_size )/2,
        20
    )
    ui.active_labels.append(enemy_map_label)
    
    
    prelogic.mymap_pos = (40, my_map_label.position[1] + 80)
    prelogic.enemymap_pos = (common.WIN_X - 40 - prelogic.enemymap_size, enemy_map_label.position[1] + 80)

    
    suurender_button = ui.ButtonInteractive(
        text="Surrender",
        position=(0,0),
        callback= surrender,
        font = ui.Font30
    )
    suurender_button.position = (
        (prelogic.mymap_pos[0] + prelogic.mymap_size + prelogic.enemymap_pos[0] - suurender_button.size_x)/2,
        prelogic.mymap_pos[1]  + prelogic.mymap_size + 40
    )
    ui.active_buttons.append(suurender_button)
    
    prelogic.turn_label = ui.Label(
        text="", 
        position= (
            (prelogic.mymap_pos[0] + prelogic.mymap_size + prelogic.enemymap_pos[0])/2,
            my_map_label.position[1]
        ),
        font=ui.Font32
    )
    ui.active_labels.append(prelogic.turn_label)
    
    prelogic.my_left_label = ui.Label(
        text = "left:",
        position=(0,0),
        font= ui.Font36
    )
    prelogic.my_left_label.position = (
        (suurender_button.position[0] - prelogic.my_left_label.size_x)/2,
        suurender_button.position[1] 
    )
    ui.active_labels.append(prelogic.my_left_label)
    
    prelogic.enemy_left_label = ui.Label(
        text = "left:",
        position=(0,0),
        font= ui.Font36
    )
    prelogic.enemy_left_label.position = (
        (suurender_button.position[0] + suurender_button.size_x + common.WIN_X - prelogic.enemy_left_label.size_x)/2,
        suurender_button.position[1] 
    )
    ui.active_labels.append(prelogic.enemy_left_label)
    
    left_labels_update()
    
    if eventhandler.ActiveConnection.is_server:
        game.game.turn = 0
    else:
        game.game.turn = 1
    
    if (game.game): set_turn(game.game.turn)
    
def game_menu_update():
    if common.mouse_button_down and common.mouse_button==1:
        if game.game and game.game.turn==0:
            mouse_ipos = (
                (common.mouse_pos[0]-prelogic.enemymap_pos[0])//prelogic.enemymap_tilesize, 
                (common.mouse_pos[1]-prelogic.enemymap_pos[1])//prelogic.enemymap_tilesize
            )
            if common.inrange(mouse_ipos[0], 0, 9) and common.inrange(mouse_ipos[1], 0, 9):
                make_move(mouse_ipos[0], mouse_ipos[1])

def game_menu_deinit():
    prelogic.looking_game_results = False
    prelogic.turn_label = None

def game_update():
    all_update()
    if (game.last_gamestate != game.gamestate):
        ui.active_buttons.clear()
        ui.active_labels.clear()
        if (game.last_gamestate!=None): prelogic.LOG(game.last_gamestate + " DEINIT")
        match game.last_gamestate:
            case common.GameState.CHOOSE_MODE_MENU:
                choose_mode_menu_deinit()
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
            case common.GameState.CHOOSE_MODE_MENU:
                choose_mode_menu_init()
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
        case common.GameState.CHOOSE_MODE_MENU:
            choose_mode_menu_update()
        
        case common.GameState.MAIN_MENU:
            main_menu_update()
        
        case common.GameState.PREPARING_MENU:
            preparing_menu_update()
        
        case common.GameState.GAME_MENU:
            game_menu_update()
        
        case _:
            pass
        
