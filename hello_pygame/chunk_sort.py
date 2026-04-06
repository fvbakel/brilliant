def compare(v1,v2):
    if v1 == v2:
        return 0
    if v1 < v2:
        return -1
    return 1

class ChunkSorter():

    def __init__(self,numbers):
        self.numbers = numbers
        self.main_chunk = Chunk()

    def sort(self):
        for num in self.numbers:
            self.main_chunk.add_value(num)
        result = self.main_chunk.get_values()
        return result


class Chunk:

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
        
if __name__ == "__main__":
    import random
    import sys
    import time




    nr_of_nrs = 100
    if len(sys.argv) > 1:
        nr_of_nrs = int(sys.argv[1])

    print(f'nr of numbers = {nr_of_nrs}')

    numbers = [ num for num in range(nr_of_nrs)]
    random.shuffle(numbers)
    
    if nr_of_nrs < 100:
        print(f"Input: {numbers}")

    sorter = ChunkSorter(numbers)
    start = time.perf_counter()
    result = sorter.sort()
    end = time.perf_counter()
    print(f"Duration Chunk sorter {end - start}")

    if nr_of_nrs < 100:
        print(f"Output: {result}")

    start = time.perf_counter()
    result = sorted(numbers)
    end = time.perf_counter()
    print(f"Duration sorted {end - start}")
    


    
