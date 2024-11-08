import random
from timeit import default_timer as timer



class Box:

    def __init__(self,box_number:int):
        self.box_number     = box_number
        self.points_to_box  = None
        self.visited        = False

class PrisonSimulation:

    def __init__(self,nr_of_prisoners:int):
        start = timer()
        if nr_of_prisoners % 2 != 0:
            raise ValueError(f'Assumed only even number of prisoners {nr_of_prisoners} is not even')
        self.nr_of_prisoners = nr_of_prisoners
        self.max_loop_size = self.nr_of_prisoners // 2
        self.base_array = list(range(0,self.nr_of_prisoners))
        self.boxes:list[Box] = []
        for n in self.base_array:
            self.boxes.append(Box(n))

        self.current_simulation = 0
        self.times_escaped      = 0
        self.times_not_escaped  = 0

        end = timer()
        print(f'Init ready, took {end - start} sec')

    def run_sim(self,nr_of_times):
        for i in range(0,nr_of_times):
            self.run_once()

    def shuffle(self):
        start = timer()
        random.shuffle(self.base_array)
        end = timer()
        print(f'shuffle, took {end - start} sec')
        start = timer()
        
        #for box_num,prison_num in enumerate(self.base_array):
        #    self.boxes[box_num].points_to_box = self.boxes[prison_num]
        #    self.boxes[box_num].visited = False
        for n,box in enumerate(self.boxes):
            box.points_to_box = self.boxes[self.base_array[n]]
            box.visited = False
        
        end = timer()
        print(f'reset, took {end - start} sec')

    def run_once(self):
        start = timer()

        self.current_simulation += 1
        self.shuffle()
        end_shuffle = timer()
        if self.has_loop_longer_than_max():
            self.times_not_escaped  += 1
        else:
            self.times_escaped +=1
        # ...
        end = timer()
        print(f'Prisoners escaped {self.times_escaped} out of {self.current_simulation} took {end - start } seconds reset took {end_shuffle - start}')

    def next_not_visited(self):
        for box in self.boxes:
            if not box.visited:
                return box
        return None

    def has_loop_longer_than_max(self):
        total_checked = 0
        while True:
            next_start = self.next_not_visited()
            if next_start is None:
                raise Exception('This should not never happen, some program error maybe?')

            loop_size = self.find_loop_size(next_start)
            if loop_size >= self.max_loop_size:
                return True
            total_checked += loop_size
            if total_checked > self.max_loop_size:
                return False


    def find_loop_size(self, next_start:Box):
        loop_size = 0
        while True:
            if next_start.visited:
                break
            next_start.visited = True
            loop_size += 1
            next_start = next_start.points_to_box
        return loop_size


def main():
    sim = PrisonSimulation(1_000_000)
    sim.run_sim(nr_of_times=1)

if __name__ == '__main__':
    main()