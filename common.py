VERSION = "1.0.0"

import sys
import os

cwd = os.getcwd()

sys.path.append(cwd+'/tasks/')
import tasks.task as task

import socket
import time
import json

import pygame


RUN = True
def STOP():
    global RUN
    RUN = False

WIN_X,WIN_Y = 1280, 720
RES_FORM = (WIN_X, WIN_Y)
FPS = 60

class MessageType:
    BROADCAST = 'BROADCAST' # udp
    REQUEST_CONN = 'REQUEST_CONN' # udp
    ANSWER_CONN = 'ANSWER_CONN' # udp
    
    CHECK_CONN = 'CHECK_CONN' # tcp
    APPROVE_CONN = 'APPROVE_CONN' # tcp
    GAME_EVENT = 'GAME_EVENT' # tcp
    GAME_SYNC = 'GAME_SYNC'

class GameEventType:
    READY = 'READY'
    UNREADY = 'UNREADY'
    ASK_READY = 'ASK_READY'
    
    START_GAME = 'START_GAME'
    QUIT_GAME = 'QUIT_GAME' # leave before the end
    END_GAME = 'END_GAME'
    
    MAKE_MOVE = 'MAKE_MOVE'
    
    MOVE_EMPTY = 'MOVE_EMPTY'
    MOVE_SHOT = 'MOVE_SHOT'
    MOVE_KILLED = 'MOVE_KILLED'

class GameState:
    MAIN_MENU = 'MAIN_MENU'
    PREPARING_MENU = 'PREPARING_MENU'
    GAME_MENU = 'GAME_MENU'
    
pygame.init()
pygame.mixer.init()


wn = pygame.display.set_mode((WIN_X,WIN_Y), vsync=1)
RES_CURRENT = (WIN_X, WIN_Y)


pygame.display.set_caption("seawolf")

clock = pygame.time.Clock()


window = pygame.Surface((RES_FORM[0], RES_FORM[1]))
background = pygame.Surface((RES_FORM[0], RES_FORM[1]))

DefaultFont = pygame.font.Font(pygame.font.match_font('timesnewroman'), 18)
def draw_text(text, x, y, surf = window, font = DefaultFont, color=(0,0,0)):
    surf.blit(font.render(text,True,color), (x,y))

def color_inverse(color: tuple[int,int,int]):
    return (255-color[0], 255-color[1], 255-color[2])

class Label:
    def __init__(self, text, position, center=False, font=DefaultFont, fontcolor=(0,0,0), backcolor=(235,235,235),
                 add=None):
        self.text = text
        self.position = position
        self.center = center
        
        self.font = font
        self.fontcolor = fontcolor
        self.backcolor = backcolor
        (self.text_size_x, self.text_size_y) = self.font.size(self.text)
        self.size_x = self.text_size_x*1.2
        self.size_y = self.text_size_y*1.2
        if center:
            self.size_x = min(self.size_x, self.text_size_x+20)
            self.size_y = min(self.size_y, self.text_size_y+10)
        
        self.add = add # additional info (not used in class)
        
    def draw(self, surf:pygame.Surface):
        pygame.draw.rect(surf, self.backcolor, pygame.Rect(self.position[0], self.position[1], self.size_x, self.size_y), border_radius=2)
        text_x = self.position[0] + 0.1*self.size_x
        text_y = self.position[1] + 0.1*self.size_y
        if self.center:
            text_x = self.position[0] + self.size_x/2 - self.text_size_x/2
            text_y = self.position[1] + self.size_y/2 - self.text_size_y/2
        draw_text(self.text, text_x, text_y, font=self.font, surf=surf, color=self.fontcolor)
        
    def set_text(self, newtext: str):
        self.text = newtext
        (self.text_size_x, self.text_size_y) = self.font.size(self.text)


active_labels: list[Label] = []

class MessageBox(Label):
    def __init__(self, message, timeout, center=True, font=DefaultFont, fontcolor=(0,0,0), backcolor=(220,220,220), add=None):
        super().__init__(
            text= message,
            position=(0,0),
            center=center,
            font=font,
            fontcolor=fontcolor,
            backcolor=backcolor,
            add=add
        )
        self.size_y += 3
        
        self.timeout = timeout
        self.created = time.time()
        
    def draw(self, surf:pygame.Surface, x:int, y:int):
        pygame.draw.rect(surf, self.backcolor, pygame.Rect(x, y, self.size_x, self.size_y), border_radius=2)
        
        text_x = x + 0.1*self.size_x
        text_y = y + 0.1*self.size_y
        if self.center:
            text_x = x + self.size_x/2 - self.text_size_x/2
            text_y = y + self.size_y/2 - self.text_size_y/2
        
        draw_text(self.text, text_x, text_y, font=self.font, surf=surf, color=self.fontcolor)
        
        timefull = 1 - (time.time() - self.created)/self.timeout
        pygame.draw.rect(surf, color_inverse(self.backcolor), pygame.Rect(x, y + self.size_y*0.9, self.size_x*timefull, self.size_y*0.1), border_radius=1)

MBs: list[MessageBox] = []

EVENTS: list[pygame.event.Event] = []

mouse_clicked: bool = False
mouse_pos: tuple[int, int] = (0,0)
mouse_button: int = None

def inrange(value, vmin, vmax) -> bool:
    if (value >= vmin and value <= vmax): return True
    return False

def ERROR(message: str, duration: float=5):
    message = "ERROR: " + message
    MBs.append(MessageBox(message, duration, fontcolor=(255,0,0)))

LOGS_ENABLED = False

def LOG(message: str, duration: float=3):
    global LOGS_ENABLED
    message = "LOG: " + message
    if LOGS_ENABLED: 
        MBs.append(MessageBox(message, duration, backcolor=(200,200,200)))
        
def INFO(message: str, duration: float=3):
    global LOGS_ENABLED
    message = "INFO: " + message
    MBs.append(MessageBox(message, duration))
    
    


class ButtonInteractive(Label):
    def __init__(self, text, position, callback, center=True, oneclick=False, font=DefaultFont, fontcolor=(0,0,0), backcolor=(210,210,220),
                 add=None):
        super().__init__(text, position, center, font, fontcolor, backcolor, add)
        self.callback = callback
        self.clicks = 0
        self.oneclick = oneclick
    
    def avtivate(self):
        if (self.oneclick and self.clicks>0):
            return
        if (self.callback != None): self.callback()
        self.clicks += 1


active_buttons: list[ButtonInteractive] = []