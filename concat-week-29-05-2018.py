'''
https://brilliant.org/weekly-problems/2018-05-28/intermediate/?p=5



'''


def calculate(x):
    strs = str(x)
    total = 0
    for istr in strs:
        i = int(istr)
        total += i **3
    return total

def appendToLimitSet(limitSet,calculatedMap,x):
    limitSet[x] = calculatedMap[x]
    if calculatedMap[x] not in limitSet:
        appendToLimitSet(limitSet,calculatedMap,calculatedMap[x])

def calculateLimitSet(limitSet,calculatedMap,x):
    if x in calculatedMap:
        if x not in limitSet:
            appendToLimitSet(limitSet,calculatedMap,x)
        return
    else:
        total = calculate(x)
        calculatedMap[x] = total
        calculateLimitSet(limitSet,calculatedMap,total)
    
def calculateLimitSetSum(max):
    limitSet = {}
    for x in range (0,max):
        calculatedMap = {}
        calculateLimitSet(limitSet,calculatedMap,x)

    print('calculatedMap=',calculatedMap)
    print('limitSet=',limitSet) 
    print('Sum limitSet=',sum(limitSet.values()))
    return sum(limitSet.values())

def test_all_functions():
    calculatedMap = {}
    limitSet = {}
    total = calculate(123)
    print('total=',total)
    calculateLimitSet(limitSet,calculatedMap,3)
    print('calculatedMap=',calculatedMap)
    print('limitSet=',limitSet)
    limitSet = {}
    calculateLimitSet(limitSet,calculatedMap,4)
    print('calculatedMap=',calculatedMap)
    print('limitSet=',limitSet)
    calculateLimitSetSum(10)
    calculateLimitSetSumCycle(2)

def calculateLimitSetSumCycle(maxTries):
    i =1
    last = 0
    val = 10
    while i < maxTries:
        total =  calculateLimitSetSum(val)
        if last == total:
            print('Total sum is:', total)
            break
        i +=1
        val = val *10
        last = total

test_all_functions()
calculateLimitSetSumCycle(6)
    

