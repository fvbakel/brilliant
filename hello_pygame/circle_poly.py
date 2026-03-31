#
# See https://www.patternsgameprog.com/series/discover-python-and-patterns/
# https://www.patternsgameprog.com/discover-python-and-patterns-12-command-pattern

import os
import pygame

os.environ['SDL_VIDEO_CENTERED'] = '1'

class GameState():
    def __init__(self):
        self.x = 120
        self.y = 120
        self.radius_max=300
        self.radius_min=10
        self.r = self.radius_min
        self.growing=True
        self.size_change= False

    def update(self,moveCommandX,moveCommandY,togle_change_size):
        self.x += moveCommandX
        self.y += moveCommandY

        if togle_change_size:
            self.size_change = not self.size_change

        if self.size_change:
            if self.growing:
                self.r = self.r + 1
            else:
                self.r = self.r - 1
            if self.r == self.radius_max:
                self.growing = False
            if self.r == self.radius_min:
                self.growing = True
        

class UserInterface():
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((640,480))
        pygame.display.set_caption("Discover Python & Patterns - https://www.patternsgameprog.com")
        #pygame.display.set_icon(pygame.image.load("icon.png"))
        self.clock = pygame.time.Clock()
        self.gameState = GameState()
        self.running = True
        self.moveCommandX = 0
        self.moveCommandY = 0
        self.change_size = False

    def processInput(self):
        self.moveCommandX = 0
        self.moveCommandY = 0
        self.change_size = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    self.moveCommandX = 8
                elif event.key == pygame.K_LEFT:
                    self.moveCommandX = -8
                elif event.key == pygame.K_DOWN:
                    self.moveCommandY = 8
                elif event.key == pygame.K_UP:
                    self.moveCommandY = -8
                elif event.key == pygame.K_a:
                    self.change_size = True

    def update(self):
        self.gameState.update(self.moveCommandX,self.moveCommandY,self.change_size)

    def render(self):
        self.window.fill((0,0,0))
        x = self.gameState.x
        y = self.gameState.y
        r = self.gameState.r
        pygame.draw.circle(self.window,color=(0,0,255),center=(x,y),radius=r,width=2)
        pygame.display.update()    

    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(60)

userInterface = UserInterface()
userInterface.run()

pygame.quit()