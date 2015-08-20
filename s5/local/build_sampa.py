from __future__ import print_function#, unicode_literals

import maryclient
import codecs
import common_utils
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Retrieves pronounciations entries of arbitrary German words (using the TTS software Mary) for a whole word list.')
    parser.add_argument('-i', '--inputfile', dest='inputfile',
                        help='Process this word list (one per line, utf-8)', type=str, default='')
    parser.add_argument('-o', '--outputfile', dest='outputfile',
                        help='Export pronouciation entries to this outputfile (one per line, utf-8)', type=str, default='')
    args = parser.parse_args()
    
    mary = maryclient.maryclient()
    dictionary = {}
    with codecs.open(args.inputfile, 'r', 'utf-8') as inputfile:
        for word in inputfile:
            tokens, phonems = common_utils.getCleanTokensAndPhonemes(
                word, mary)
            if len(phonems) != 1:
                print(
                    'Warning, MARY did split this word into more than one token:', word, phonems)
            dictionary[word[:-1]] = ''.join(phonems[0])
    
    with codecs.open(args.outputfile, 'w', 'utf-8') as outputfile:
        for word in sorted(dictionary):
            outputfile.write(word+' '+dictionary[word]+'\n')
