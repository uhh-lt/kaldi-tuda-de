# -*- coding: utf-8 -*-

# Copyright 2015 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import common_utils
import codecs
import traceback
import datetime
import sys
import cPickle as pickle
from itertools import groupby

from bs4 import BeautifulSoup

import collections

from functools import partial

# See http://www.bas.uni-muenchen.de/Bas/BasSAMPA for more infos on German pronounciation format. However not all files adhere 100% to this specification. Parsing is made a bit more challenging since there are units that have 2 or 3 characters, but the ponounciation string is not segmented. 

BAS_German_set ={
    'vowels' : ['a:', 'a', 'e:', 'e', 'E:', 'i:', 'i', 'I', 'o:', 'o', 'O', 'u:', 'u', 'U', 'y:', 'y', 'Y', 'E', '2:', '2', '9'],
    'nasal_vowels' : ['a~:','a~','E~:', 'E~', 'O~:','O~', '9~:', '9~'],
    'diphtongs' : ['aI', 'aU', 'OY'],
    'unstressed_vowels' : ['@','6'],
    'consonants_and_stops' : ['ts','z', 'S', 'Z', 'C', 'x', 'N', 'b', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', '?', 'R','T'], #R and T are english phonemes, maybe they should also be mapped to their closesed German representations (?)
# Note we use ? as glottal stop, some BAS dictionaries use Q instead. Compare e.g. "Anfang" in Mary and BAS.
    'ignore' : ['#','+','-',','],
    'silence' : ['usb']
    }

BAS_German_set['items'] = BAS_German_set['nasal_vowels']+BAS_German_set['diphtongs']+BAS_German_set['unstressed_vowels']+BAS_German_set['vowels']+BAS_German_set['consonants']

#Diacritics
#
#503 Lengthening Length Mark         (Vowel):    
#501 Primary Stress  Vertical Stroke(Superior)   '(Vowel)
#502 Second. Stress  Vertical Stroke(Inferior)   "(Vowel)
#406 Glottalization  Subscript Tilde         q(Item)
#424 Nasalization    Superposed Tilde        (Item)~

BAS_German_set['primary'] = ["'" + item for item in BAS_German_set['items']] 
BAS_German_set['secondary'] = ['"' + item for item in BAS_German_set['items']]

# Few variants that we map to a canocial representation and boundary markers that we ignore
# Also: Maps the English phoneme w to the Germen phoneme v

# We map the glottal stop to ?, like in the MARY TTS lexicon

BAS_German_trans = {'o~':'O~', 'e~':'E~', 'q':'?' , 'Q':'?', '#':'','+':'','-':'','w':'v','D':'d'}

#These are used to translate ascii codings of german Umlaute to unicode
latex_to_unicode = {u'"U':u'Ü',u'"A':u'Ä',u'"O':u'Ö',u'"u':u'ü',u'"a':u'ä',u'"o':u'ö',u'"s':u'ß',u'-$':u'',u'$':u'',u'’':u"'"}
ascii_umlaute_to_unicode = {u'ue':u'ü',u'ae':u'ä',u'oe':u'ö',u'Ue':u'Ü',u'Ae':u'Ä',u'Oe':u'Ö'}

#German alphabet for words (+ some extra chars from other languages). Special chars - ' and . can also appear in words. 
alphabet_de = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜöäüß-'.1234567890éèçàáíōšțúłėčęαβγććâêó"

#Frequency of manual entries. Manual entries are usually better than automatic ones. 100 is a good starting point, but this variable is not tuned - experiment with it if you want.
manual_freq = 100

#example file format for data/local/dict/extra_questions.txt from Kaldi docu (http://kaldi.sourceforge.net/data_prep.html):
#
#SIL SPN NSN 
#S UW T N K Y Z AO AY SH W NG EY B CH OY JH D ZH G UH F V ER AA IH M DH L AH P OW AW HH AE R TH IY EH 
#UW1 AO1 AY1 EY1 OY1 UH1 ER1 AA1 IH1 AH1 OW1 AW1 AE1 IY1 EH1 
#UW0 AO0 AY0 EY0 OY0 UH0 ER0 AA0 IH0 AH0 OW0 AW0 AE0 IY0 EH0 
#UW2 AO2 AY2 EY2 OY2 UH2 ER2 AA2 IH2 AH2 OW2 AW2 AE2 IY2 EH2 

def BASpron_to_list(pron,word=''):
    '''takes a BAS pron string and turns it into a list of phoneme tokens'''
    orig_pron = pron

    for orig,rep in BAS_German_trans.iteritems():
        pron = pron.replace(orig,rep)

    def consume(symbols, string):
        for symbol in symbols:
            if string.startswith(symbol):
                #could consume symbol
                return True,symbol,string[len(symbol):]
        #no symbol matches start of string
        return False,'',string

    #order in which symbols are consumed
    symbol_sets = [BAS_German_set['silence'],BAS_German_set['items_glottal'],BAS_German_set['primary'],BAS_German_set['secondary'],BAS_German_set['items']]

    pron_list = []

    while len(pron) > 0:
        consumed_any = False
        for symbols in symbol_sets:
            consumed,symbol,pron = consume(symbols, pron)
            if consumed:
                consumed_any = True
                pron_list.append(symbol)
                break
        if not consumed_any:
            #try ignore list
            consumed,symbol,pron = consume(BAS_German_set['ignore'], pron)
            if not consumed:
                print 'Warning, omitting unkown symbol',pron[0],' in pronounciation list:',orig_pron,'word:',word
                pron = pron[1:]
    return pron_list

def importSampa(myid,word_substitution_dict={},withFreq=True,manual=False,delimiter='\t'):
    '''Import sampa dictionary fileformat, each line has word and its main pronounciation. A variant of this format also includes frequencies'''
    with codecs.open(myid,'r','utf-8') as inputFile:
        myinput = inputFile.read().split('\n')
        phoneme_dict = collections.defaultdict(list)

        lineerror = False
        no_lineerrors = 0

        #file format is simple and we can process it line by line
        for line in myinput:
            #ignore comments and empty lines
            if line.startswith('#') or len(line) == 0:
                continue
            if line[0].isdigit():
                print 'Info: Ignoring this line that starts with a number:',line
                continue

            #remove carriage return, if it slipped into the line
            line = line.replace('\r','')
            split = line.split(delimiter)

            #parse word and frequency (if used) and pronounciation
            word = ''
            if withFreq: 
                if (len(split)==3):
                    if lineerror:
                        print 'Last',no_lineerrors,'lines had wrong format'

                    no_lineerrors,lineerror = 0,False
                    word,freq = split[0],split[1]
                    
                    pron_list = BASpron_to_list(split[2],word)
                else:
                    print 'Encountered line with wrong format (doesnt have 3 elements)',line
            else:
                if (len(split)==2):
                    if lineerror:
                        print 'Last',no_lineerrors,'lines had wrong format'

                    no_lineerrors,lineerror = 0,False
                    word = split[0]
                    freq = 1

                    if manual==True:
                        freq = manual_freq

                    pron_list = BASpron_to_list(split[1],word)
                else:
                    if not lineerror:
                        print 'Encountered line with wrong format (doesnt have 2 elements)',line
                    lineerror = True
                    no_lineerrors += 1

            #some (older) dialects of this fileformat use e.g. a latex format for special characters. Word_substitution_dict (parameter of this function) can be used to take care of such translations.
            for orig,replace in word_substitution_dict.iteritems():
                word = word.replace(orig,replace)

            #check if we still have non-german characters
            for ch in word:
                if ch not in alphabet_de:
                    print 'Warning, encountered non-german character',ch,'in word: ',line

            if word != '':
                phoneme_dict[word] += [{'pron':pron_list,'freq':int(freq),'manual':manual}]

        if lineerror:
            print 'Last',no_lineerrors,'lines had wrong format'

        return phoneme_dict

def importBASWordforms(myid,latexCodes=True):
    '''Importer for BAS Wordforms, a dictionary fileformat which includes pronounciation variants.'''
    global phoneme_dict,meta,last_word
    with codecs.open(myid,'r','utf-8') as inputFile:
        myinput = inputFile.read().split('\n')

        def addWord(line):
            #only global to parent function
            global phoneme_dict,meta,last_word
            #convert german latex characters to unicode
            for latex,uni in latex_to_unicode.iteritems():
                line = line.replace(latex,uni)

            #check if we got all strange characters
            for ch in line:
                if ch not in alphabet_de:
                    print 'Warning, encountered non-german character',ch,'in word: ',line

            if line != '':
                phoneme_dict[line] = []
                meta[line] = []
                last_word = line
            else:
                print '[addWord] WARNING, line is empty!'
            #next state
            return 'parseMeta'

        def parseMeta(line):
            global phoneme_dict,meta,last_word
            #todo parse meta
            #OR:vm  TP:manu_veri
            return 'parsePron'

        def parsePronounciation(line):
            global phoneme_dict,meta,last_word
            if line == '*':
                #next state
                return 'addWord'
            split = line.split('\t')
           
            freq = 1

            #manual entries
            if len(split) == 1:
                pron = line
                freq = manual_freq
                manual = True
            else: # automatic entries with frequencies
                pron = split[0]
                freq = split[1]
                manual = False

            pron_list = BASpron_to_list(pron)
            if last_word != '':
                phoneme_dict[last_word] += [{'pron':pron_list,'freq':int(freq),'manual':manual}]
            else:
                print '[parsePron] empty last_word!'

            #state in this function next time
            return 'parsePron'

        phoneme_dict = {}
        meta = {}
        last_word = ''

        #simple fsa parser
        state_func = {'addWord':addWord, 'parseMeta':parseMeta,'parsePron':parsePronounciation} 
        state = 'addWord'

        for line in myinput:
            state = state_func[state](line.strip())

        return phoneme_dict

def missingImporter(filename):
    print 'No importer for',filename,'review build_big_lexicon.py. '

def guessImportFunc(filename):
    '''Guess importer based on filename. Each dictionary has a slightly different file format. But all use some variant of German (BAS) Sampa for ponounciations.'''
   
    #Standard replace rules for words
    subs_dict = {u'’':u"'"}
    #VM.German.Wordforms RVG1_trl.lex and LEXICON.TBL are available from ftp://ftp.bas.uni-muenchen.de/pub/BAS/
    if filename.endswith('VM.German.Wordforms'):
        return importBASWordforms
    elif filename.endswith('RVG1_trl.lex'):
        return partial(importSampa, word_substitution_dict=latex_to_unicode, manual=True, withFreq=False, delimiter='\t')
    elif filename.endswith('RVG1_read.lex'):
        return partial(importSampa, word_substitution_dict=ascii_umlaute_to_unicode, manual=True, withFreq=False, delimiter='\t')
    elif filename.endswith('LEXICON.TBL'):
        return partial(importSampa, word_substitution_dict=subs_dict, withFreq=True, delimiter='\t')
    #de.txt is from DFKI; under LGPL and can be downloaded from the mary project https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt
    elif filename.endswith('de.txt'):
        return partial(importSampa, word_substitution_dict=subs_dict, manual=True, withFreq=False, delimiter=' ')
    #Train.txt is generated by MARY TTS and generates phoneme entries for all words in the corpus. They will get low probability (1%) if manual entries exist.
    elif filename.endswith('train.txt'):
        return partial(importSampa, word_substitution_dict=subs_dict, manual=False, withFreq=False, delimiter=' ')
    else:
        return missingImporter

#find same pronouciations in the list and merge them
def collapsePronList(pron_list):
    #sort by pronounciation
    pron_list.sort(key=lambda elem: ''.join(elem['pron']))
    pron_list_collpased = []
    #see http://stackoverflow.com/questions/773/how-do-i-use-pythons-itertools-groupby
    for key, group in groupby(pron_list, lambda x: ' '.join(x['pron'])):
        same_prons = list(pron for pron in group)
        freq = sum([pron['freq'] for pron in same_prons])
        manual = any([pron['manual'] for pron in same_prons])
        pron_list_collpased.append({'pron':same_prons[0]['pron'],'freq':freq,'manual':manual})
    return pron_list_collpased 

def merge_dicts(d1, d2):
    '''Merge two pronounciation dictionaries'''
    for word in d2.keys():
        merged_pron_list = []
        pron_list1 = d1[word] if word in d1 else []
        pron_list2 = d2[word]

        merged_pron_list = collapsePronList(pron_list1 + pron_list2)

        #check merged list:
        for entry1 in merged_pron_list:
            if len([entry2 for entry2 in merged_pron_list if entry1['pron']==entry2['pron']])>1:
                print 'WARNING, duplicate pronounciation entry:',entry1['pron']
                print pron_list1
                print pron_list2

        d1[word] = merged_pron_list
    return d1 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Prepares various sources of pronounciations and builds a lexicon that can be exported to KALDI')
    parser.add_argument('-f', '--filelist', dest='filelist', help='Process this file list of lexicons', type=str, default = '')
    parser.add_argument('-s', '--single-file', dest='singlefile', help='Process this single lexicon file', type=str, default = '')
    parser.add_argument('-e', '--export-pickle', dest='export', help='Export pickle file of combined phoneme dictionary', type=str, default = '')
    parser.add_argument('-d', '--export-dir', dest='export_dir', help='Export dir for nonsilence_phones.txt, silence_phones.txt and extra_questions.txt' , type=str, default='data/local/dict/')

    args = parser.parse_args()

    if(args.singlefile != ''):
        ids = [args.singlefile]
    else:
        if args.filelist == '':
            print 'No files specified for processing!'
            sys.exit()
        ids = common_utils.loadIdFile(args.filelist)

    combinedDict = {}
    
    for myid in ids:
        print "I'm now opening ", myid
        importer = guessImportFunc(myid)
        d = importer(myid)
        combinedDict = merge_dicts(combinedDict, d)

    variants = 0
    for key in sorted(combinedDict.iterkeys()):
        #print 'Word:',key,combinedDict[key]
        variants += len(combinedDict[key])
        
    print 'Dictionary size is ', len(combinedDict), ' pronounciation variants ', variants

    #export dictionary to intermediate format
    pickle.dump( combinedDict, open( args.export, 'wb' ) )

    #export auxillary files
    print 'writing to', args.export_dir + 'nonsilence_phones.txt'     
    with open(args.export_dir + 'nonsilence_phones.txt','w') as nonsilence_phones:
        for item in BAS_German_set['items']:
            nonsilence_phones.write(item + " '" + item + ' "' + item + '\n')

    print 'writing to', args.export_dir + 'silence_phones.txt'
    with open(args.export_dir + 'silence_phones.txt','w') as silence_phones:
        silence_phones.write('\n'.join(BAS_German_set['silence'])+'\n')

    print 'writing to', args.export_dir + 'optional_silence.txt'
    with open(args.export_dir + 'optional_silence.txt','w') as silence_phones:
        silence_phones.write(BAS_German_set['silence'][0])

    print 'writing to', args.export_dir + 'extra_questions.txt'
    with open(args.export_dir + 'extra_questions.txt','w') as extra_questions:
        extra_questions.write(' '.join(BAS_German_set['items']) + '\n')
        extra_questions.write(' '.join(BAS_German_set['primary']) + '\n')
        extra_questions.write(' '.join(BAS_German_set['secondary']) + '\n')
    print 'done'
