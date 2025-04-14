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