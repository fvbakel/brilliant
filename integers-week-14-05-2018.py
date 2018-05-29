'''
https://brilliant.org/weekly-problems/2018-05-14/intermediate/?p=5

01234567891011
The above is the beginning of all non-negative integers concatenated into a single infinite string.

 111 is the first sub-string with 3 identical digits in a row, with different digits preceding and following the run of the identical digits. 
 The first 1  of 111 comes at position 13 (from left) in the infinite string.

Where is the first such sub-string with 4 identical digits?

eg:
Solution found at 11
01234567891011
Sequence = 111
position is = 0

'''



max =10001
find_nr = 4

concat = ''

for i in range(0,max):
    # search back to find all the same
    concat +=str(i)
    tmp = str(i-1) + str(i) +str(i+1)
    seq = ''
    p = ''
    found = False
    for c in tmp[:-1]:
        if c == p:
            seq +=c
            if len(seq) == find_nr:
                found = True
            elif len(seq) > find_nr:
                print('at %s found to long sequence %s' % (i,seq))
                found = False
        else:
            if len(seq) == find_nr:
                concat +=str(i+1)
                break
            seq = c
        p = c
    
    if found:
        loc = concat.find(seq)
        print('Solution found at',i)
        with open('solution.txt', 'w') as f: 
            f.write(concat)
            f.write('\n')
            print('Solution found at',i,file=f)
            print('Sequence =', seq,file=f)
            print('position is =', loc+1,file=f)
        print (concat)
        print('Sequence =', seq)
        print('position is =', loc+1)
        break


    

