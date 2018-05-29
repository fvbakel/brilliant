import numpy as numpy

def calculate(n):
    max =n
    y1 = 0
    y2= 0
    y3 = 0
    for i in range(1,max):
        y1 += n**i
        y2 += i**n
        y3 = y1 / y2
  #  print('%s: %s,%s,%4.4f' %(n,y1,y2,y3))
    print('%s: %4.4f' %(n,y3))

if __name__ == "__main__":
    calculate(2)
    calculate(10001)