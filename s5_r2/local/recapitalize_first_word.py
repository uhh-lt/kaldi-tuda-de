import sys

for line in sys.stdin:
    split = line.split()
    if len(split[1]) > 0:
        split[1] = split[1][0].upper() + split[1][1:]
        print(' '.join(split))
    else:
        print(line)
