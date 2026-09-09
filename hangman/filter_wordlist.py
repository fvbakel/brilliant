import re

wordlist_file = "/home/fvbakel/tmp/basiswoorden-gekeurd.txt"
wordlist_filtered = "/home/fvbakel/tmp/basiswoorden-gekeurd-filtered.txt"

replace_map = {
    'é' : 'e',
    'è' : 'e',
    'ë' : 'e',
    'ï' : 'i',
    'à' : 'a'
}

can_not_handle = set()

reg_ex = re.compile('^[a-z]+$')

def replace(word:str):
    result = ''
    for c in word:
        if c in replace_map:
            c = replace_map[c]
        else:
            if not reg_ex.fullmatch(c):
                can_not_handle.add(c)
        result = result + c
    return result

def main():
    with open(wordlist_file, "r") as input:
        with open(wordlist_filtered, "w") as output:
            for line in input:
                if line is None:
                    continue
                word = line.strip()
                # 
                if reg_ex.fullmatch(word):
                    output.write(f"{word}\n")
                else:
                    word = replace(word)
                    if reg_ex.fullmatch(word):
                        output.write(f"{word}\n")
                
    print(can_not_handle)
                                         

if __name__ == '__main__':
    main()