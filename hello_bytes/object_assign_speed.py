from timeit import default_timer as timer
import random

class MyObject():
    
    def __init__(self):
        self.a_bool = True
        self.other_obj = None

def main():
    my_list:list[MyObject] = []
    n = 1_000_000
    for i in range(0,n):
        my_list.append(MyObject)

    my_frozen_list = tuple(my_list)
    
    list_two = list(range(0,n))
    random.shuffle(list_two)
    
    start = timer()
    for n,obj in enumerate(my_list):
        obj.a_bool = False
        obj.other_obj = my_frozen_list[list_two[n]]
    end = timer()
    print(f'Took {end - start} sec')
    

if __name__ == '__main__':
    main()