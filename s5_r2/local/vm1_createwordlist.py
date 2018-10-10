replace_rules = {'"s':'ß','"a':'ä','"u':'ü', '"o':'ö', '"A':'Ä','"U':'Ü', '"O':'Ö', '<':'', '>':'', '-$':'', '$-':'', '$':'', '-':'' , '\'' : '' }

wordlist = []

with open('data/vm_lexicon_ids.txt', 'r') as lexicon_ids:
    for line in lexicon_ids:
        if line[-1] == '\n':
            line = line[:-1]
        print("reading:", line)
        if line != '':
            with open(line) as inputfile:
                for inputline in inputfile:
                    word = inputline.split()[0]
                    for rule in replace_rules.items():
                        word = word.replace(rule[0],rule[1])
                    wordlist.append(word)

wordlist = list(set(wordlist))

with open('data/local/g2p/vm_wordlist.txt', 'w') as outfile:
    for word in sorted(wordlist):
        outfile.write(word + '\n')
