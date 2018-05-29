''' briliant week of 14 may



'''
from math import cos, radians

                
def calculate_cos_sum(start=0):
    total = 0
    for i in range(0, 360):
        angle = start + i
        total += cos(radians(angle)) 
    return total


if __name__ == '__main__':
    for i in range(1, 360):
        print("calculate_cos_sum(%s)=%4.2f" % (i,  calculate_cos_sum(i)))
