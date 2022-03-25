import sys

# Also change some very frequent words to new ortographic rules in German
# e.g. muß -> muss
word_replace_rules = {'muß':'muss', 'daß':'dass', 'Daß':'dass', '-$':' ', '-$':' ', '$':'', '$':'', '-':'' , '  ' : ' '}

for line in sys.stdin:
    line = line.replace('Das', 'das')
    # remove ähs, ähms and unks as well as hesitations (häs)
    line = line.replace('Äh', '').replace('äh', '').replace('Ähm', '').replace('ähm', '').replace('häs', '').replace('<UNK>', '').replace('<unk>', '')
    split = line.split()
    if len(split) > 1:
        if len(split[1]) > 1:
            split[1] = split[1][0].upper() + split[1][1:]
            output = ' '.join(split)
        elif len(split[1]) == 1:
            split[1] = split[1][0].upper()
            output = ' '.join(split)
        else:
            #if we have issues just pass the line unchanged
            output = line

        for replace_rule in word_replace_rules.items():
            output = output.replace(replace_rule[0], replace_rule[1])
        print(output)

    else:
        #if we have issues just pass the line unchanged
        print(line)
