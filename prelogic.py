import game # type: ignore

from game import ui
from game import connection
from game import common # type: ignore
from common import task
# connection = game.connection
# common = game.common
# task = common.task


def ERROR(message: str, duration: float=5):
    message = "ERROR: " + message
    ui.MBs.append(ui.MessageBox(message, duration, fontcolor=(255,0,0)))

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


MYUSERNAME = connection.LOCAL_INFO[0]
MYADRRESS = [ip for ip in connection.LOCAL_INFO[2] if not ip.startswith("127.")]

print(MYADRRESS, MYUSERNAME)

UDP: connection.UDP_Sock | None = None
TCP: connection.TCP_Sock | None = None

open_hosts: list[str] = [] #adresses
open_hosts_buttons: list[ui.ButtonInteractive] = []
open_hosts_page_label: ui.Label | None = None
open_hosts_page = 0
open_hosts_onepage = 5
open_hosts_update_task: task.ThreadTask | None = None
open_hosts_selfhost_label = None