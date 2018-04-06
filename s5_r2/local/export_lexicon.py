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
import cPickle as pickle
import codecs

#generate string for one entry of the dictionary
def generateEntry(word,entry,sphinx_format=False):
    freqMult = 0.0
    #find most frequent entry
    freqs = [pron['freq'] for pron in entry]
    freqMult = 1.0 / float(max(freqs))
    freqs = [float(pron['freq'])*freqMult for pron in entry]
    
    txt = ''
    for i,(freq,elem) in enumerate(sorted(zip(freqs,entry),reverse=True)):
        if sphinx_format:
            txt += word + ('('+str(i)+')' if i>0 else '') + '  ' + ' '.join(elem['pron']) + '\n'
        else:
            #Kaldi probabilty format <word> <freq> <pronounciation>
            txt += word + ' ' + str(freq) + ' ' + ' '.join(elem['pron']) + '\n'
    return txt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the TUDA corpus (XML) into text transcriptions for KALDI')
    parser.add_argument('-f', '--file', dest='file', help='process this (python pickle) lexicon file', type=str)
    parser.add_argument('-o', '--outfile', dest='outfile', help='lexicon out file', type=str, default='lexiconp.txt')
    parser.add_argument('-sph', '--sphinx-format', dest='sphinx_format', help='export lexicon in sphinx format', action='store_true', default=False)

    args = parser.parse_args()

    print 'Load ', args.file

    combinedDict = pickle.load( open( args.file , 'rb' ) )
    
    with codecs.open(args.outfile,'w','utf-8') as outfile:
        if '%' in combinedDict:
            combinedDict['<UNK>'] = combinedDict['%']
            print '<UNK> is:', combinedDict['<UNK>']
            #del combinedDict['%']
        else:
            'Warning!: No % entry found! Will add <UNK> -> usb mapping manually.'
            combinedDict['<UNK>'] = [{'pron': ['usb'], 'freq': 100, 'manual': True}]
        for key in sorted(combinedDict.iterkeys()):
            txt = generateEntry(key,combinedDict[key],args.sphinx_format)
            outfile.write(txt)

