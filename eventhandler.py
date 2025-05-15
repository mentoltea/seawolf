# from common import *
# import prelogic
# import messages # type: ignore
import time

import bot
from bot import messages
from messages import prelogic
from prelogic import connection

class EventHandler:
    @staticmethod
    def connection_requested(username: str, addr: tuple[str,str]):
        prelogic.LOG("Connection requested" + " : " + addr[0])
    
    @staticmethod
    def connection_accepted():
        pass
    
    @staticmethod
    def connection_rejected():
        pass
    
    @staticmethod
    def preparation_enemy_ready():
        pass
    
    @staticmethod
    def preparation_enemy_unready():
        pass
    
    @staticmethod
    def preparation_ready_asked():
        pass
    
    @staticmethod
    def game_sync_requested():
        pass
    
    @staticmethod
    def game_start():
        pass
    
    @staticmethod
    def game_quit():
        pass
    
    @staticmethod
    def game_end():
        pass
    
    @staticmethod
    def game_my_move_empty():
        pass
    @staticmethod
    def game_my_move_shot():
        pass
    @staticmethod
    def game_my_move_killed():
        pass
    
    @staticmethod
    def game_enemy_move_empty():
        pass
    @staticmethod
    def game_enemy_move_shot():
        pass
    @staticmethod
    def game_enemy_move_killed():
        pass
    
    
    @staticmethod
    def quit():
        pass



ActiveConnection: connection.TCP_Sock | bot.Bot_Sock | None = None
LastCheckedConnection: float = time.time()


def safesend(connection: connection.TCP_Sock | bot.Bot_Sock | None, message: str | bytes) -> bool:
    if (connection == None):
        return False
    try:
        connection.send(message)
        return True
    except Exception as e:
        prelogic.LOG("Unable to send message")
        print(str(e))
        return False
