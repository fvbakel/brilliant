import math
import random
import numpy as np
import time
import matplotlib.pyplot as plt
from typing import Any, List, Tuple, Set, Dict, Sequence, Iterator, Iterable, Generator
from collections import defaultdict, Counter, deque
from itertools import product, islice, chain
from operator import itemgetter
import doctest

def f(x):
    return (x*x) -2

def f_derived(x):
    return 2*x

def bisection_method(f,start_a:float,start_b:float,precision=0.001,max_step=10):
    
    if start_a > start_b:
        raise("a must be smaller than b")
    
    f_a = f(start_a)
    f_b = f(start_b)
    if f_a < 0 and f_b < 0:
        raise("f(a) and f(b) are both negative, one must be positive, other negative ")
    elif f_a > 0 and f_b > 0:
        raise("f(a) and f(b) are both positive, one must be positive, other negative ")

    current_step = 0
    a = start_a
    b = start_b
    while current_step < max_step:
        current_step += 1
        mid_point_c = (a + b ) / 2
        f_c = f(mid_point_c)
        print(f"Step {current_step} a = {a} b = {b} mid_point_c = {mid_point_c} f_c = {f_c}")
        # end conditions
        if f_c == 0:
            print(f"Stopped at condition 0 in step {current_step} a = {a} b = {b} mid_point_c = {mid_point_c} f_c = {f_c}")
        elif abs(start_a - mid_point_c) < precision:
            print(f"Stopped at condition 1 in step {current_step} a = {a} b = {b} mid_point_c = {mid_point_c} f_c = {f_c}")
            return mid_point_c
        elif abs(f_a - f_c) < precision:
            print("Stopped at condition 2")
            return mid_point_c
        
        # next iteration
        if (f_a < 0 and f_c < 0) or (f_a > 0 and f_c > 0):
             a = mid_point_c
             f_a = f_c
        else:
            b = mid_point_c
            f_b = f_c
    print("Stopped at max iterations")
    return None


def main():
    print("Start")
    root_estimate = bisection_method(f = f,
                                     start_a = -1,
                                     start_b = 10,
                                     precision= 0.1,
                                     max_step= 10)
    print(f"Found  root_estimate = {root_estimate}")
    print("End")


if __name__ == "__main__":
    main()
