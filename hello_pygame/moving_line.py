#
# See https://www.patternsgameprog.com/series/discover-python-and-patterns/
# https://www.patternsgameprog.com/discover-python-and-patterns-12-command-pattern

import os
import pygame
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'


class GameState():
    def __init__(self):
        self.lines = []
        self.circles = []
        self.max_x = 640
        self.max_y = 480
        
class Simulation:

    def __init__(self,game_state: GameState):
        self.game_state = game_state
        
        self.center = (200,200)
        self.radius = 150

        self.game_state.lines.append([self.center,self.center])
        self.game_state.circles.append((self.center,self.radius))
        self.angle = 90

    def update_game_state(self):

        self.angle -= 1
        new_x = self.center[0] + (math.cos(math.radians(self.angle)) * self.radius)
        new_y = self.center[1] - (math.sin(math.radians(self.angle)) * self.radius)

        self.game_state.lines[0][1] = (new_x,new_y)
        pass

class UserInterface():
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption("Line experiments")
        
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.simulation = Simulation(self.game_state)

        self.window = pygame.display.set_mode((self.game_state.max_x,self.game_state.max_y))

        
        self.running = True

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break

    def simulate_step(self):
        self.simulation.update_game_state()

    def render(self):
        self.window.fill((0,0,0))

        for (p1,p2) in self.game_state.lines:
            pygame.draw.line(self.window,color=(0,0,255),start_pos=p1,end_pos=p2,width=3)

        for center,radius in self.game_state.circles:
            pygame.draw.circle(self.window,color=(0,0,255),center=center,radius=radius,width=2)

        pygame.display.update()    

    def run(self):
        while self.running:
            self.process_input()
            self.simulate_step()
            self.render()
            self.clock.tick(120)
            

userInterface = UserInterface()
userInterface.run()

pygame.quit()