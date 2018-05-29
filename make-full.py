formula = ''

for i in range(1, 21):
	append  = '(x^{0}-{0})'.format(i)
	formula = '{0}{1}'.format(formula, append)

print (formula)	
#with open('formula.txt', 'w') as the_file:
#    the_file.write(formula)

total = 0
for i in range(1, 21):
	total = total + i
	print (i, total)	
	
