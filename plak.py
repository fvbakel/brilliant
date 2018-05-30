'''
	y|x = y(x|y) 

    In this formula | concatenates two numbers. eg 1|2 =12 and 11|3=113
		
    posible values for x must meet:
        n          2
    (x = 10    * y - y    ) / (10 * y - 1)
    
    conditions:
    x must be a number
    0 >= y < 10

    for a given y, what is the value for x?

'''

def check(y, x):
    success = False

    try:
        left = str(y) + str(x)
        right = str(y * int ( str(x) + str(y)  ) )
        
        if left == right:
            success = True
    except BaseException as e:
        print ("Error in check!", repr(e))

    return success

def calculate():
    for y in range(0,10):
        solution = findSmallestSolution(y)
        if solution is not None:
            print ("Found solution for y=%s, x=%s " % (y , solution) )
        else: 
            print ("No solution for y=", y )

def findSmallestSolution(y):
    solution = None
    
    y2 = y **2
    tens = 1
    noemer = 10 * y - 1
    x = 0
    n = 0
    while n < 100:
        n += 1
        tens = tens * 10
        teller = tens *y
        teller = teller - y2
       
        remainder = teller % noemer
        if remainder == 0:
            x = teller//noemer
            if check(y,x):
                solution = x
                break

    return solution

if __name__ == '__main__':
    calculate()