import random
import json
import typing
import time

import messages
from messages import prelogic
from prelogic import game
from messages import common


# abstraction for bot
class Bot_Sock:
    def __init__(self, is_server:bool):
        self.is_server: bool = is_server
        self.connected: bool = True
        
        self.messages_to_send: list[str] = []
        self.messages_to_send.append(messages.ready_message())
        
        
        self.gamestate: str = common.GameState.PREPARING_MENU
        self.game = game.GameClass()
        
        
        self.bot_is_server = not self.is_server
        if self.bot_is_server:
            self.set_turn(0)
        else:
            self.set_turn(1)
        
        remaining_ships = sorted(game.SHIPS_COUNT.copy().items(), reverse=True)
        for (l, c) in remaining_ships:
            for _ in range(c):
                while True:
                    ix = random.randint(0, 9)
                    iy = random.randint(0, 9)
                    orient = random.randint(0, 1)
                    if (game.canPlaceShip(self.game, self.game.editmap, l, ix, iy, orient)):
                        game.placeShip(self.game, self.game.editmap, l, ix, iy, orient)
                        break
        
        # self.messages_to_send.append(messages.ready_message())
    
    def __del__(self):
        pass

    def stop(self):
        self.connected = False

    def set_turn(self, turn: int):
        self.game.turn = turn
    
    # recv for bot                    
    def send(self, message:str|bytes):
        if (not self.connected): return
        
        
        if (isinstance(message, str)):
            rcv = message.encode("utf-8")
        else:
            rcv = message
        rcv: bytes = bytes( rcv )
        
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
                        continue
                    
                    case common.MessageType.GAME_EVENT:
                        event: dict[str, typing.Any] = jsondata["event"]
                        etype: str = event["type"]
                        match (etype):
                            case common.GameEventType.READY:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                self.game.opponent_ready = True
                                
                            case common.GameEventType.UNREADY:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                self.game.opponent_ready = False
                                
                            case common.GameEventType.ASK_START_GAME:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                self.game.opponent_ready = True
                                # eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_appr_message())
                                self.messages_to_send.append(messages.start_game_appr_message())
                            
                            case common.GameEventType.START_GAME_DECLINE:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                self.game.opponent_ready = False
                                
                            case common.GameEventType.START_GAME_APPROVE:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                                                
                                # eventhandler.safesend( eventhandler.ActiveConnection, messages.start_game_sappr_message())
                                self.messages_to_send.append(messages.start_game_sappr_message())
                                # game.set_gamestate(common.GameState.GAME_MENU)
                                self.gamestate = common.GameState.GAME_MENU
                                
                                self.game.mymap = self.game.editmap.copy()
                                self.game.my_ships = self.game.edit_ships.copy()
                                
                                self.game.enemymap = game.empty_map(game.CellType.UNKNOWN)
                                self.game.enemy_ships = []
                            
                            case common.GameEventType.START_GAME_SECOND_APPROVE:
                                if (self.gamestate != common.GameState.PREPARING_MENU): continue
                                
                                # game.set_gamestate(common.GameState.GAME_MENU)
                                self.gamestate = common.GameState.GAME_MENU
                                
                                self.game.mymap = self.game.editmap.copy()
                                self.game.my_ships = self.game.edit_ships.copy()
                                
                                self.game.enemymap = game.empty_map(game.CellType.UNKNOWN)
                                self.game.enemy_ships = []
                            
                            # ------------------------------------------------------------------
                            
                            case common.GameEventType.SURRENDER_GAME:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                self.connected = False                            
                                
                            case common.GameEventType.END_GAME:
                                if (self.gamestate != common.GameState.GAME_MENU): continue

                                # eventhandler.safesend(eventhandler.ActiveConnection, messages.end_game_message())
                                self.messages_to_send.append(messages.end_game_message())
                                self.connected = False
                            
                            # ------------------------------------------------------------------
                            
                            case common.GameEventType.MAKE_MOVE:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if (self.game):
                                    cell = self.game.mymap[iy][ix]
                                    match cell:
                                        case game.CellType.HIDDEN:
                                            # eventhandler.safesend( eventhandler.ActiveConnection, messages.move_empty_message(move))
                                            self.messages_to_send.append(messages.move_empty_message(move))
                                            game.set_move_mymap(self.game, self.game.mymap, ix, iy, game.CellType.EMPTY)
                                            self.set_turn(0)

                                        case game.CellType.BOAT:
                                            self.game.mymap[iy][ix] = game.CellType.SHOT
                                            if (game.isKilled(self.game, self.game.mymap, ix, iy)):
                                                # eventhandler.safesend( eventhandler.ActiveConnection, messages.move_killed_message(move))
                                                self.messages_to_send.append(messages.move_killed_message(move))
                                                game.set_move_mymap(self.game, self.game.mymap, ix, iy, game.CellType.KILLED)
                                                
                                            else:
                                                # eventhandler.safesend( eventhandler.ActiveConnection, messages.move_shot_message(move))
                                                self.messages_to_send.append(messages.move_shot_message(move))
                                                game.set_move_mymap(self.game, self.game.mymap, ix, iy, game.CellType.SHOT)
                                            self.set_turn(1)
                                        
                                        case _:
                                            prelogic.LOG(move + " " + str(cell))
                                            # eventhandler.safesend( eventhandler.ActiveConnection, messages.bad_move_message(move))
                                            self.messages_to_send.append(messages.bad_move_message(move))
                            
                            case common.GameEventType.MOVE_EMPTY:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if self.game:
                                    game.set_move_enemymap(self.game, self.game.enemymap, ix, iy, game.CellType.EMPTY)
                                self.set_turn(1)
                                
                            case common.GameEventType.MOVE_SHOT:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if self.game:
                                    game.set_move_enemymap(self.game, self.game.enemymap, ix, iy, game.CellType.SHOT)
                                self.set_turn(0)
                            
                            case common.GameEventType.MOVE_KILLED:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                
                                move: str = event["move"]
                                (ix, iy) = game.pos2xy(move)
                                if self.game:
                                    game.set_move_enemymap(self.game, self.game.enemymap, ix, iy, game.CellType.KILLED)
                                self.set_turn(0)
                            
                            case common.GameEventType.BAD_MOVE:
                                if (self.gamestate != common.GameState.GAME_MENU): continue
                                prelogic.INFO("BOT: Bad move")
                                prelogic.LOG("BOT: Bad move")
                                self.set_turn(0)
                            
                            
                            case _:
                                prelogic.LOG(f"Unknown event type {etype}")
                        
                    
                    case _:
                        prelogic.LOG(f"Unknown message type {mtype}")
                
            except Exception as e:
                prelogic.ERROR(str(e))
                print(data)
                return

    # send for bot
    def recv(self, timeout:float=1, buffsize:int=4096) -> bytes | None:
        if (not self.connected): return
        
        if (self.game.turn == 0 and self.gamestate==common.GameState.GAME_MENU):
            self.make_move()
        
        final_message = ""
        for i, m in enumerate(self.messages_to_send):
            if (len(final_message + m) >= buffsize): break
            else: 
                final_message += m
                self.messages_to_send.pop(i)
        
        if (final_message==""): return None
        
        # simulating thinking
        time.sleep( (0.6 + 0.4 * random.random()) * timeout )
        
        return final_message.encode("utf-8")
    
    def move_is_valid(self, ix: int, iy: int) -> bool:
        if (self.game.enemymap[iy][ix] != game.CellType.UNKNOWN): return False
        return True
    
    def make_move(self):
        ix, iy = 0, 0
        while True:
            ix = random.randint(0,9)
            iy = random.randint(0,9)
            if (self.move_is_valid(ix, iy)):
                break    
        
        # eventhandler.safesend(eventhandler.ActiveConnection, messages.make_move_message(game.xy2pos(ix, iy)))
        self.messages_to_send.append(messages.make_move_message(game.xy2pos(ix, iy)))
        self.set_turn(2)