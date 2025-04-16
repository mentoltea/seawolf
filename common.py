import typing
import version # type: ignore
import sys
import os

cwd = os.getcwd()

sys.path.append(cwd+'/tasks/')
import tasks.task as task # type: ignore

import socket # type: ignore
import time
import json # type: ignore

import pygame


RUN: bool = True
def STOP():
    global RUN
    RUN = False # type: ignore

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


wn = pygame.display.set_mode((WIN_X,WIN_Y), pygame.SRCALPHA, vsync=1)
RES_CURRENT = (WIN_X, WIN_Y)


pygame.display.set_caption("seawolf")

clock = pygame.time.Clock()


window = pygame.Surface((RES_FORM[0], RES_FORM[1]), pygame.SRCALPHA)
background = pygame.Surface((RES_FORM[0], RES_FORM[1]), pygame.SRCALPHA)

DefaultFont = pygame.font.Font(pygame.font.match_font('timesnewroman'), 18)
def draw_text(text: str, x: float, y: float, surf: pygame.Surface = window, font: pygame.font.Font = DefaultFont, color:tuple[int,int,int]=(0,0,0)):
    surf.blit(font.render(text,True,color), (x,y))

def color_inverse(color: tuple[int,int,int]):
    return (255-color[0], 255-color[1], 255-color[2])

class Label:
    def __init__(self, text: str, position: tuple[float,float], center:bool=False, font:pygame.font.Font=DefaultFont, 
                 fontcolor:tuple[int,int,int]=(0,0,0), backcolor:tuple[int,int,int]=(235,235,235),
                 add: typing.Any =None):
        self.text = text
        self.position = position
        self.center = center
        
        self.font = font
        self.fontcolor = fontcolor
        self.backcolor = backcolor
        (self.text_size_x, self.text_size_y) = self.font.size(self.text)
        self.size_x: float = self.text_size_x*1.2
        self.size_y: float = self.text_size_y*1.2
        if center:
            self.size_x = min(self.size_x, self.text_size_x+20)
            self.size_y = min(self.size_y, self.text_size_y+10)
        
        self.add = add # additional info (not used in class)
        
    def draw(self, surf:pygame.Surface, *args : typing.Any, **kwargs: typing.Any):
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
    def __init__(self, message:str, timeout:float, center:bool=True, font:pygame.font.Font=DefaultFont, 
                 fontcolor:tuple[int,int,int]=(0,0,0), backcolor:tuple[int,int,int]=(220,220,220), 
                 add:typing.Any=None):
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

    def draw(self, surf:pygame.Surface, x:float, y:float):
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
mouse_button: int | None = None

def inrange(value: typing.Any, vmin: typing.Any, vmax: typing.Any) -> bool:
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
    def __init__(self, text: str, position: tuple[int,int], 
                 callback: typing.Callable[[], None] | task.BasicTask | task.MultyTask | None,
                 center:bool=True, oneclick:bool=False, font:pygame.font.Font=DefaultFont, 
                 fontcolor:tuple[int,int,int]=(0,0,0), backcolor:tuple[int,int,int]=(210,210,220),
                 add:typing.Any=None):
        super().__init__(text, position, center, font, fontcolor, backcolor, add)
        self.callback = callback
        self.clicks = 0
        self.oneclick = oneclick
    
    def avtivate(self):
        if (self.oneclick and self.clicks>0):
            return
        if (self.callback != None): self.callback()
        self.clicks += 1
    
    def click_check(self, x: float, y: float):
        if (inrange(x, self.position[0], self.position[0] + self.size_x) and inrange(y, self.position[1], self.position[1] + self.size_y)):
            self.avtivate()
            # print("click button")
            return True
        return False


active_buttons: list[ButtonInteractive] = []


class Dialog:
    def __init__(self,
                 text: str,
                 button_left: ButtonInteractive | None = None,
                 button_right: ButtonInteractive | None = None,
                 timeout : float = float('inf'),
                 on_timeout_call : typing.Callable[[], None] | None = None):
        self.label = Label(text=text, 
                           position=(0,0), 
                           center=True)
        
        self.backcolor = tuple(map(lambda v: max(0, v), list(self.label.backcolor)))
        
        self.button_count = 0
        button_size_x : float = 10
        button_size_y : float = 10
        
        
        self.button_center: ButtonInteractive | None = None
        
        
        self.button_left = button_left
        if (button_left != None):
            self.button_count += 1
            button_size_x += button_left.size_x
            button_size_y += button_left.size_y
        
        self.button_right = button_right
        if (button_right != None):
            self.button_count += 1
            button_size_x += button_right.size_x
            if (button_left == None):
                button_size_y += button_right.size_y
        
        if (self.button_count == 1):
            self.button_center = self.button_left if self.button_left != None else self.button_right
        
        self.timeout = timeout
        self.created_at = time.time()
        self.on_timeout_call = on_timeout_call
        
        self.content_size_x = max(self.label.size_x, button_size_x)
        self.content_size_y = self.label.size_y + button_size_y + 10

        self.size_x = min(self.content_size_x*1.1, self.content_size_x + 10*2)
        self.size_y = min(self.content_size_y*1.1, self.content_size_y + 10*2)

        x = (WIN_X - self.size_x)/2
        y = (WIN_Y - self.size_y)/2
        
        self.label.position = (
            x + self.size_x/2 - self.label.size_x/2,
            y + 10,
        )
        if (self.button_center != None):
            self.button_center.position = (
                x + self.size_x/2 - self.button_center.size_x/2,
                y + self.size_y - self.button_center.size_y - 10,
            )
        elif (self.button_left != None and self.button_right != None):
            self.button_left.position = (
                x + 10,
                y + self.size_y - self.button_left.size_y - 10,
            )
                
            
            self.button_right.position = (
                x + self.size_x - self.button_right.size_x - 10,
                y + self.size_y - self.button_right.size_y - 10,
            )
    
    def __del__(self):
        if (self.on_timeout_call):
            self.on_timeout_call()
    
    def draw(self, surf: pygame.Surface):
        x = (WIN_X - self.size_x)/2
        y = (WIN_Y - self.size_y)/2
        
        # surf.fill((200,200,200,0))
        pygame.draw.rect(surf, self.backcolor, pygame.Rect(x, y, self.size_x, self.size_y), border_radius=2, width=2)
        
        
        self.label.draw(surf)
        
        if (self.button_count == 1):
            self.button_center.draw(window) # type: ignore
        elif (self.button_count == 2):
            self.button_left.draw(window) # type: ignore
            self.button_right.draw(window) # type: ignore
                
        timefull = 1 - (time.time() - self.created_at)/self.timeout
        pygame.draw.rect(surf, color_inverse(self.label.backcolor), pygame.Rect(x, y + self.size_y*0.95, self.size_x*timefull, self.size_y*0.05), border_radius=1)

    def click_check(self, x: float, y: float):
        # print("click")
        if ((self.button_left and self.button_left.click_check(x, y)) 
            or (self.button_right and self.button_right.click_check(x, y))):
            self.timeout = 0
            # print("clicked")

active_dialog: Dialog | None = None
dialogs: list[Dialog] = []