import typing # type: ignore
import version # type: ignore
import sys
import os

cwd = os.getcwd()

sys.path.append(cwd+'/tasks/')
import tasks.task as task # type: ignore

import socket # type: ignore
import time # type: ignore
import json # type: ignore

import pyautogui
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

RES_CURRENT = (WIN_X, WIN_Y)
# os.environ['SDL_VIDEO_WINDOW_POS'] = "200,200"
# wn = pygame.display.set_mode(RES_CURRENT, pygame.SRCALPHA, vsync=1)
pygame.display.set_caption("seawolf")



clock = pygame.time.Clock()


window = pygame.Surface((RES_FORM[0], RES_FORM[1]), pygame.SRCALPHA)

EVENTS: list[pygame.event.Event] = []

mouse_clicked: bool = False
mouse_pos: tuple[int, int] = (0,0)
mouse_button: int | None = None

def inrange(value: typing.Any, vmin: typing.Any, vmax: typing.Any) -> bool:
    if (value >= vmin and value <= vmax): return True
    return False

def change_window_size(newsize: tuple[int,int]):
    global WIN_X, WIN_Y, RES_CURRENT, RES_FORM, wn, window, shift_WINX, shift_WINY
    (WIN_X, WIN_Y) = newsize # type: ignore
    RES_FORM = newsize # type: ignore
    RES_CURRENT = newsize # type: ignore
    shift_WINX = newsize[0] - WIN_X
    shift_WINY = newsize[1] - WIN_Y
    
    pygame.display.quit()

    (desc_x, desc_y) = pyautogui.size()
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{desc_x//2 - WIN_X//2},{desc_y//2 - WIN_Y//2}"
    
    wn = pygame.display.set_mode(RES_CURRENT, pygame.SRCALPHA, vsync=1)
    window = pygame.Surface((RES_FORM[0], RES_FORM[1]), pygame.SRCALPHA)

change_window_size(RES_CURRENT)