wordlist_filtered = "/home/fvbakel/tmp/basiswoorden-gekeurd-filtered.txt"

def main():
    lengths = dict()
    with open(wordlist_filtered, "r") as input:
        for line in input:
            if line is None:
                continue
            word = line.strip()
            l = len(word)
            if l not in lengths:
                lengths[l] = 0
            lengths[l] += 1
    
    for l in sorted(lengths.keys()):
        print(f'{l} : {lengths[l]}')

if __name__ == '__main__':
    main()