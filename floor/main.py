import math
import random


def runOnce():
	x = random.uniform(1, 1000)
	y = random.uniform(1, 1000)

	xa = math.floor( x )
	ya = math.floor( y )

	z = x + y
	za = math.floor( z )

	zb = xa + ya

#	print('x floor({0})) = {1}'.format(x,xa))
#	print('y floor({0})) = {1}'.format(y,ya))
#	print('z floor({0})) = {1}'.format(z,za))

#	print('floor (x + y ) = {0}   floor (x) + floor (y) =  {1} '.format(za,zb))
	
	return (za == zb)

def runN(n):
	equal = 0
	for i in range(0, n):
		if (runOnce()):
			equal = equal + 1
	return equal

nr_of_runs= 1000000
	
result = runN(nr_of_runs)

print ('For nr_of_runs={0}  result={1}'.format(nr_of_runs,result))
