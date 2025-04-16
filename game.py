# enemy map:
# 0 - unknown cell
# 1 - empty cell
# 2 - shot cell
# 3 - killed cell

# my map:
# 0 - unknown cell (doesnt exists)
# 1 - empty cell
# 2 - shot cell
# 3 - killed cell


# import common
import connection
common = connection.common

ALPLABET = 'abcdefghij'
SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
last_gamestate = None
gamestate = common.GameState.MAIN_MENU


def empty_map(default=0) -> list[list[int]]:
    return [[default for j in range(10)] for i in range(10)]

def ispos(pos: str) -> bool:
    if len(pos) != 2: return False
    if pos[0] not in ALPLABET: return False
    if not pos[1].isdigit(): return False
    return True

def pos2xy(pos: str):
    literal = pos[0].lower()
    num = int(pos[1])
    return ALPLABET.find(literal), num

def xy2pos(x:int, y:int) -> str:
    literal = ALPLABET[x]
    return literal + str(y)


class GameClass:
    
    def __init__(self):
        # self.state = GameState.PREPARING_MENU
        self.ready = False
        
        # 0 - my turn
        # 1 - enemy turn
        # hosts always moves first
        self.turn = 0
        
        self.ended = False
        
        # prepare maps
        self.editmap = empty_map(1) 
        self.tempmap = empty_map(1)
        
        # game maps
        self.mymap = empty_map(1)
        self.enemymap = empty_map(0)
        
        