'''
https://brilliant.org/weekly-problems/2018-05-21/advanced/?p=4

'''

def calculate(n):
    global count
    y = n **2
    yStr = str(y).zfill(2)
    last = yStr[-2:]
    count[last] =  count.get(last,0) + 1
    
    print('%s: %s : %s' %(n,yStr,last))

if __name__ == "__main__":
    count = {}
    for n in range(1,101):
        calculate(n)
    print (count)
    print (sum(count.values()))
    