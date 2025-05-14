
# import common
# import connection
import ui # type: ignore
from ui import connection # type: ignore
from connection import common
# common = connection.common

class CellType:
    UNKNOWN = 0
    HIDDEN = 1 # mine
    EMPTY = 2
    BOAT = 3 # mine
    SHOT = 4
    KILLED = 5

ALPHABET = 'abcdefghij'
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
        # 2 - waiting
        # hosts always moves first
        self.turn = 0
        
        self.ended = False
        
        # prepare maps
        self.editmap = empty_map(CellType.HIDDEN) 
        
        # [ship length, ship position [x,y], ship orientation]
        # orientation: 
        # 0 - horizontal
        # 1 - vertical
        self.edit_ships: list[ tuple[ int, tuple[int,int], int] ] = []
        
        # types on map:
        # 0 - unknown cell
        # 1 - empty cell
        # 2 - boat cell, not shot
        # 3 - boat cell, shot
        # 4 - boat cell, killed
        
        # game maps
        self.mymap = empty_map(CellType.HIDDEN)
        self.my_ships: list[ tuple[ int, tuple[int,int], int] ] = []
        
        self.enemymap = empty_map(CellType.UNKNOWN)
        self.enemy_ships: list[ tuple[ int, tuple[int,int], int] ] = []

def set_gamestate(newstate: str):
    global gamestate
    gamestate = newstate


def empty_map(default:int=0) -> list[list[int]]:
    return [[default for _ in range(10)] for _ in range(10)]

def ispos(pos: str) -> bool:
    if len(pos) != 2: return False
    if pos[0] not in ALPHABET: return False
    if not pos[1].isdigit(): return False
    return True

def pos2xy(pos: str):
    literal = pos[0].lower()
    num = int(str(pos[1:len(pos)]))
    return ALPHABET.find(literal), num-1

def xy2pos(x:int, y:int) -> str:
    literal = ALPHABET[x]
    return literal + str(y+1)

def cellIsAvailable(map: list[list[int]], ix: int, iy: int) -> bool:
    for dx in range(-1, 1 + 1):
        for dy in range(-1, 1 + 1):
            if not common.inrange(ix + dx, 0, 9) or not common.inrange(iy + dy, 0, 9):
                continue
            if map[iy+dy][ix+dx] != CellType.HIDDEN:
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
    gm.edit_ships.append(( l, (ix, iy), orient ))

# index
def selectShipIdx(gm: GameClass, ships: list[tuple[ int, tuple[int,int], int]], map: list[list[int]],  ix: int, iy: int) -> int:
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
    for i, s in enumerate(ships):
        if (s[1] == (cx,cy)):
            idx = i
            # ship = s
            break
    
    return idx

# ship
def selectShipS(gm: GameClass, map: list[list[int]],  ix: int, iy: int) -> tuple[ int, tuple[int,int], int]:
    if map[iy][ix] not in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
        return (0, (0,0), 0)
    cx, cy = ix, iy
    while True:
        if cx>0 and map[cy][cx-1] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cx -= 1
            continue
        elif cy>0 and map[cy-1][cx] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cy -= 1
        else:
            break
    
    l = 1
    (ix,iy) = (cx,cy)
    o = 0
    
    cx, cy = ix, iy
    while True:
        if cx<9 and map[cy][cx+1] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cx += 1
            l += 1
            o = 0
            continue
        elif cy<9 and map[cy+1][cx] in [CellType.BOAT, CellType.SHOT, CellType.KILLED]:
            cy += 1
            l += 1
            o = 1
        else:
            break
    
    return (l, (ix,iy), o)
 
def removeShip(gm: GameClass, map: list[list[int]],  idx: int) -> tuple[ int, tuple[int,int], int]:
    ship = gm.edit_ships.pop(idx)
    (l, (ix, iy), orient) = ship
    cx, cy = ix, iy
    for _ in range(l):
        map[cy][cx] = CellType.HIDDEN
        if (orient == 0):
            cx += 1
        else:
            cy += 1
    return ship
        

def isKilled(gm: GameClass, map: list[list[int]],  ix: int, iy: int) -> bool:
    idx = selectShipIdx(gm, gm.my_ships, map, ix, iy)
    if (idx==-1):
        return False
    (l, (x, y), o) = gm.my_ships[idx]
    cx,cy = x,y
    for _ in range(l):
        if map[cy][cx] == CellType.BOAT:
            return False
        if (o == 0):
            cx += 1
        else:
            cy += 1
    return True

def set_block_killed(map: list[list[int]],  ix: int, iy: int):
    map[iy][ix] = CellType.KILLED
    for dx in range(-1, 1 + 1):
        for dy in range(-1, 1 + 1):
            if not common.inrange(ix + dx, 0, 9) or not common.inrange(iy + dy, 0, 9):
                continue
            if map[iy+dy][ix+dx] in [CellType.HIDDEN, CellType.UNKNOWN]: 
                map[iy+dy][ix+dx] = CellType.EMPTY

def set_move_enemymap(gm: GameClass, map: list[list[int]],  ix: int, iy: int, m: int):
    map[iy][ix] = m
    if (m != CellType.KILLED): return
    # CellType.KILLED ->
    ship = (l, (x,y), o) = selectShipS(gm, map, ix, iy)
    print(ship)
    
    cx,cy = x,y
    for _ in range(l):
        set_block_killed(map, cx, cy)
        if (o == 0):
            cx += 1
        else:
            cy += 1
    
    gm.enemy_ships.append(ship)

def set_move_mymap(gm: GameClass, map: list[list[int]],  ix: int, iy: int, m: int):
    map[iy][ix] = m
    if (m != CellType.KILLED): return
    # CellType.KILLED ->
    idx  = selectShipIdx(gm, gm.my_ships, map, ix, iy)
    if (idx==-1): return
    (l, (x,y), o) = gm.my_ships[idx]
    cx,cy = x,y
    for _ in range(l):
        set_block_killed(map, cx, cy)
        if (o == 0):
            cx += 1
        else:
            cy += 1

game: GameClass | None = None