import sys
import os

cwd = os.getcwd()

sys.path.append(cwd+'/tasks/')
import tasks.task as task

import socket
import time
import json

import pygame

import 

RUN = True
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

DefaultFont = pygame.font.Font(pygame.font.match_font('timesnewroman'), 16)
def draw_text(text, x, y, surf = window, font = DefaultFont, color=(0,0,0)):
    surf.blit(font.render(text,True,color), (x,y))

class MessageBox:
    def __init__(self, message, font, timeout):
        self.message = message
        self.font = font
        (self.size_x, self.size_y) = self.font.size(self.message)
        self.timeout = timeout
        self.created = time.time()
        
    def draw(self, surf, x:int, y:int):
        pygame.draw.rect(surf, (25,25,25), pygame.Rect(x, y, self.size_x*1.2, self.size_y*1.2), border_radius=1)
        draw_text(self.message, x + 0.1*self.size_x, y + 0.1*self.size_y, font=self.font, surf=surf)

MBs: list[MessageBox] = []