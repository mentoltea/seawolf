import game # type: ignore

from game import ui
from game import connection
from game import common # type: ignore
from common import task
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
        ui.MBs.append(ui.MessageBox(message, duration, backcolor=(200,200,200)))
        
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

sent_requests: list[str] = [] #adresses
open_hosts: list[str] = [] #adresses
open_hosts_buttons: list[ui.ButtonInteractive] = []
open_hosts_page_label: ui.Label | None = None
open_hosts_page = 0
open_hosts_onepage = 4
open_hosts_update_task: task.ThreadTask | None = None
open_hosts_selfhost_label = None


editmap_pos = (40, 40)
editmap_tilesize = 45
editmap_size = editmap_tilesize*10
editmap_mouse_ipos = (0,0)

ready_button: ui.ButtonInteractive | None = None
opponent_ready_label: ui.Label | None = None
ready_cooldown: float = 0
max_ready_cooldown: float = 2