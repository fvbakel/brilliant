''' briliant week of 7 may

Problems of the Week Contribute a problem Week of May 7
	 	 	 
x and y are integers and xy+1 is divisible by 24

Is x+y also divisible by 24? 

'''

def find_solution():
    max =10000
    for x in range (1,max):
        for y in range (1,max):
            total = x + y
            case = (x * y) + 1
            if (not (case % 24) ):
                if  not (total % 24):
                    i=0
                    #print('Found {0} * {1} +1 = {2}  = {3} * 24   {0} + {1} = {4} = {5} * 24'.format(x,y,case,case/24,total, total/24))
                else:
                    print('Not true {0} * {1} +1 = {2}  = {3} * 24   {0} + {1} = {4} = {5} * 24'.format(x,y,case,case/24,total, total/24))
                
        


if __name__ == '__main__':


    find_solution()

    
