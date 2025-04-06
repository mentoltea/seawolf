from common import *
from logic import *



def get_trans(Surf, width, height, angle):
    return pygame.transform.rotate(pygame.transform.scale(Surf, (int(round(width)), int(round(height)))), int(round(angle)))
    #return pygame.transform.scale(pygame.transform.rotate(Surf, int(round(angle))), (int(round(width)),int(round(height))))

def window_update():
    wn.fill((0,0,0))
    window.fill((245,245,245))
    
    mb_y = 0
    for box in MBs:
        box.draw(window, 0, mb_y)
        mb_y += box.size_y
    
    wn.blit(get_trans(window, RES_CURRENT[0], RES_CURRENT[1], 0), (0,0))

