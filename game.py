
# import common
# import connection
import ui # type: ignore
from ui import connection # type: ignore
from connection import common
# common = connection.common

class CellType:
    UNKNOWN = 0
    EMPTY = 1
    BOAT = 2
    SHOT = 3
    KILLED = 4

ALPLABET = 'abcdefghij'
# SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
SHIPS_COUNT: dict[int, int] = {
    1: 4,
    2: 3,
    3: 2,
    4: 1
}
last_gamestate: str|None = None
gamestate: str = common.GameState.CHOOSE_MODE_MENU


class GameClass:
    def __init__(self):
        # self.state = GameState.PREPARING_MENU
        self.ready = False
        self.opponent_ready = False
        
        # 0 - my turn
        # 1 - enemy turn
        # hosts always moves first
        self.turn = 0
        
        self.ended = False
        
        # prepare maps
        self.editmap = empty_map(1) 
        self.tempmap = empty_map(1)
        
        # [ship length, ship position [x,y], ship orientation]
        # orientation: 
        # 0 - horizontal
        # 1 - vertical
        self.ships: list[ tuple[ int, tuple[int,int], int] ] = []
        
        # types on map:
        # 0 - unknown cell
        # 1 - empty cell
        # 2 - boat cell, not shot
        # 3 - boat cell, shot
        # 4 - boat cell, killed
        
        # game maps
        self.mymap = empty_map(1)
        self.enemymap = empty_map(0)

def set_gamestate(newstate: str):
    global gamestate
    gamestate = newstate


def empty_map(default:int=0) -> list[list[int]]:
    return [[default for _ in range(10)] for _ in range(10)]

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

def cellIsAvailable(map: list[list[int]], ix: int, iy: int) -> bool:
    for dx in range(-1, 1 + 1):
        for dy in range(-1, 1 + 1):
            if not common.inrange(ix + dx, 0, 9) or not common.inrange(iy + dy, 0, 9):
                continue
            if map[iy+dy][ix+dx] != CellType.EMPTY:
                return False
    return True

def canPlaceShip(gm: GameClass, map: list[list[int]], l: int, ix: int, iy: int, orient: int) -> bool:
    cx, cy = ix, iy
    for _ in range(l):
        if not common.inrange(cx, 0, 9) or not common.inrange(cy, 0, 9):
            return False
        if not cellIsAvailable(map, cx, cy):
            return False
        
        if (orient == 0):
            cx += 1
        else:
            cy += 1
    return True

def placeShip(gm: GameClass, map: list[list[int]], l: int, ix: int, iy: int, orient: int):
    cx, cy = ix, iy
    for _ in range(l):
        map[cy][cx] = CellType.BOAT
        if (orient == 0):
            cx += 1
        else:
            cy += 1
    gm.ships.append(( l, (ix, iy), orient ))

# index & length
def selectShip(gm: GameClass, map: list[list[int]],  ix: int, iy: int) -> int:
    if map[iy][ix] not in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
        return -1
    cx, cy = ix, iy
    while True:
        if cx>0 and map[cy][cx-1] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cx -= 1
            continue
        elif cy>0 and map[cy-1][cx] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cy -= 1
        else:
            break
    
    idx = -1
    # ship = (0, (0,0), 0)
    for i, s in enumerate(gm.ships):
        if (s[1] == (cx,cy)):
            idx = i
            # ship = s
            break
    
    return idx
            
def removeShip(gm: GameClass, map: list[list[int]],  idx: int) -> tuple[ int, tuple[int,int], int]:
    ship = gm.ships.pop(idx)
    (l, (ix, iy), orient) = ship
    cx, cy = ix, iy
    for _ in range(l):
        map[cy][cx] = CellType.EMPTY
        if (orient == 0):
            cx += 1
        else:
            cy += 1
    return ship
        
        
game: GameClass | None = None