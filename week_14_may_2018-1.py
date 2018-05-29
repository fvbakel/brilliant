import numpy as numpy

def calculatey1y2(x):
    max =20
    y1 = 1
    y2 = 0
    for i in range(1,max):
        y1 += x**i
        y2 += i * (x**i)
    print('%4.4f=%4.4f,%4.4f' %(x,y1,y2))

if __name__ == "__main__":
    step = 110
    start = 0
    stop =1
    nrs = numpy.linspace(start,stop,num=step)
    

    for x in nrs:
        calculatey1y2(x)
    
    calculatey1y2(0.5)
