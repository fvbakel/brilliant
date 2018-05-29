''' briliant week of 7 may

The first 17 positive integers are rearranged into a sequence such that the sum of any two adjacent terms is a perfect square.
What is the sum of the first and last terms of this sequence?

'''

choice_list = list(range(1,18)) 

def check_list(check_list):
    ''' check if a given list matches the creteria '''
    result = True
    
    copy_list = check_list.copy();
    previous = copy_list.pop(0)
    for num in copy_list:
        tmp = num + previous
        if not check_is_perfect_square(tmp):
            result = False
            break
        previous = num
    return result

def check_is_perfect_square(num):
    ''' check is a given number is a perfect square '''
    result = False
    candidates = list(range (1,6))
    for can in candidates:
        remain = num % can
        div = num / can
        if remain == 0 and div == can:
            result = True
            break
        
    return result

def find_sol(a_list,dept):
    ''' recursive function to find a solution '''
    global choice_list
    dept +=1
    for next_num in choice_list:
        if next_num not in a_list:
            a_list.append(next_num)
            print(dept,'Checking a_list=',a_list)
            if check_list(a_list):
                if len(a_list) == 17:
                    return True, a_list.copy()
                else:
                    found, solution = find_sol(a_list.copy(), dept)
                    if not found:
                        a_list.pop(-1)
                        #  print('Removing next num=%s, removing= %s' % (next_num, last_elem))
                    else:
                        return found, solution
            else:
                a_list.pop(-1)
    return False, a_list

def find_solution():
    global choice_list
    for start in choice_list:
        a_list = list()
        a_list.append(start)

        print('Trying with start =',start)
        dept = 0
        found, solution = find_sol(a_list, dept)
        if found:
            print('found= ', found)
            print('solution= ', solution)
            break

if __name__ == '__main__':
    print(check_is_perfect_square(9))
    print(check_is_perfect_square(8))
    print(check_list([2,7,2]))

    find_solution()

    
