import game
# import connection

connection = game.connection
common = game.common
task = common.task
eventhandler = connection.eventhandler

# import common
# import tasks.task as task
# import eventhandler


MYUSERNAME = connection.LOCAL_INFO[0]
MYADRRESS = [ip for ip in connection.LOCAL_INFO[2] if not ip.startswith("127.")]

print(MYADRRESS, MYUSERNAME)

UDP: connection.UDP_Sock | None = None

open_hosts: list[str] = [] #adresses
open_hosts_buttons: list[common.ButtonInteractive] = []
open_hosts_page_label: common.Label | None = None
open_hosts_page = 0
open_hosts_onepage = 5
open_hosts_update_task: task.ThreadTask | None = None
open_hosts_selfhost_label = None