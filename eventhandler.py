# from common import *
import common

class EventHandler:
    def connection_requested(username, addr):
        common.LOG("Connection requested" + " : " + addr[0])
    
    def connection_accepted():
        pass
    
    def connection_rejected():
        pass
    
    def preparation_enemy_ready():
        pass
    
    def preparation_enemy_unready():
        pass
    
    def preparation_ready_asked():
        pass
    
    def game_sync_requested():
        pass
    
    def game_start():
        pass
    
    def game_quit():
        pass
    
    def game_end():
        pass
    
    def game_my_move_empty():
        pass
    def game_my_move_shot():
        pass
    def game_my_move_killed():
        pass
    
    def game_enemy_move_empty():
        pass
    def game_enemy_move_shot():
        pass
    def game_enemy_move_killed():
        pass
    
    
    def quit():
        pass
    