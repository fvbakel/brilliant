#
# See https://www.patternsgameprog.com/series/discover-python-and-patterns/
# https://www.patternsgameprog.com/discover-python-and-patterns-12-command-pattern
import os
import pygame
import random

os.environ['SDL_VIDEO_CENTERED'] = '1'

nr_of_compares = 0
def compare(v1,v2):
    global nr_of_compares
    nr_of_compares = nr_of_compares + 1
    if v1 == v2:
        return 0
    if v1 < v2:
        return -1
    return 1

class BaseSort():
    def __init__(self,numbers: list[int]):
        self.numbers = numbers
        self.ready = False
        self.swapped = False
        self.step = 0

    def _is_ready(self):
        return False

    def _swap(self,i,j):
        org = self.numbers[i]
        self.numbers[i] = self.numbers[j]
        self.numbers[j] = org
        self.swapped = True

    def do_step(self):
        pass

class BubbleSort(BaseSort):

    def __init__(self,numbers: list[int]):
        super().__init__(numbers)
        self.current_index = 0
        self.current_max_index = len(self.numbers) -1


    def _is_ready(self):
        if self.current_max_index == 0:
            self.ready = True
            return True

        if self.current_index == self.current_max_index and not self.swapped:
            self.current_max_index == 0
            self.ready = True
            return True

    def do_step(self):
        self.step += 1
        if self._is_ready():
            print(f'Ready in step {self.step}')
            return
        if self.current_index == self.current_max_index:
            self.current_index = 0
            self.current_max_index = self.current_max_index - 1
            self.swapped = False

        if self.numbers[self.current_index] > self.numbers[self.current_index + 1]:
            self._swap(self.current_index,self.current_index + 1)
            
        self.current_index  +=1 

class CocktailSort(BaseSort):

    def __init__(self,numbers: list[int]):
        super().__init__(numbers)
        self.current_min_index = 1
        self.current_max_index = len(self.numbers) -1
        self.current_index = 0
        self.going_up = True

    def _is_ready(self):
        if self.current_max_index == 0:
            self.ready = True
            return True

        if self.current_index == self.current_max_index and not self.swapped and self.going_up:
            self.current_max_index == 0
            self.ready = True
            return True

    def do_step(self):
        self.step += 1
        if self._is_ready():
            print(f'Ready in step {self.step}')
            return
        if self.going_up:
            self._do_step_up()
        else:
            self._do_step_down()
    
    def _do_step_up(self):
        if self.current_index == self.current_max_index:
            self.current_max_index = self.current_max_index - 1
            self.swapped = False
            self.going_up = False
            self._do_step_down()

        if self.numbers[self.current_index] > self.numbers[self.current_index + 1]:
            self._swap(self.current_index,self.current_index + 1)
        self.current_index += 1 
    
    def _do_step_down(self):
        if self.current_index == self.current_min_index:
            self.current_min_index = self.current_min_index + 1
            self.swapped = False
            self.going_up = True
            self._do_step_up()

        if self.numbers[self.current_index] < self.numbers[self.current_index - 1]:
            self._swap(self.current_index,self.current_index - 1)
        self.current_index -= 1 

class ChunkSort(BaseSort):

    def __init__(self,numbers: list[int]):
        super().__init__(numbers)
        self.numbers = numbers
        self.main_chunk = Chunk()
        self.current_index = 0
        self.ready = False


    def sort(self):
        for num in self.numbers:
            self.main_chunk.add_value(num)
        result = self.main_chunk.get_values()
        return result

    def do_step(self):
        if self.ready:
            return
        
        self.main_chunk.add_value(self.numbers[self.current_index])

        for index,val in enumerate(self.main_chunk.get_values()):
            self.numbers[index]=val

        self.current_index +=1
        if self.current_index == len(self.numbers):
            print("Ready")
            print(f'Number of compares {nr_of_compares}')
            self.ready = True


class Chunk():

    def __init__(self):
        self.mid_values = []
        self.left_chunk = None
        self.right_chunk = None
        self.compare = compare

    def add_value(self,value):
        if len(self.mid_values) == 0:
            self.mid_values.append(value)
            return
        
        result = self.compare(value,self.mid_values[0])
        if  result == 0:
            self.mid_values.append(value)
            return
        elif result == -1:
            if self.left_chunk is None:
                self.left_chunk = Chunk()
            self.left_chunk.add_value(value)
            return
        else:
            if self.right_chunk is None:
                self.right_chunk = Chunk()
            self.right_chunk.add_value(value)
            return
        
    def get_values(self):
        result = []
        if self.left_chunk is not None:
            result = result + self.left_chunk.get_values()
        result = result + self.mid_values
        if self.right_chunk is not None:
            result = result + self.right_chunk.get_values()

        return result


class GameState():
    def __init__(self):
        self.lines = []
        self.circles = []
        self.max_x = 200
        self.max_y = self.max_x
        
class Simulation:

    def __init__(self,game_state: GameState):
        self.game_state = game_state
        self.numbers = [ num for num in range(self.game_state.max_x )]
        random.shuffle(self.numbers)
        self.game_state.lines = []
        for index, number in enumerate(self.numbers):
            self.game_state.lines.append([(index,self.game_state.max_y),(index,self.game_state.max_y - number)])
        
        # CocktailSort, BubbleSort, ChunkSort
        self.sorter = ChunkSort(self.numbers)

    def update_game_state(self):
        if self.sorter.ready:
            return
        self.sorter.do_step()
        for index, number in enumerate(self.numbers):
            self.game_state.lines[index][1] = (index,self.game_state.max_y - number)

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
            self.clock.tick(0)
            

userInterface = UserInterface()
userInterface.run()

pygame.quit()