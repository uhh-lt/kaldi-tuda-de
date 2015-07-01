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

import os
import errno
import maryclient

from bs4 import BeautifulSoup

import itertools

def loadIdFile(idfile,remove_extension='.wav',use_no_files=-1):
    ids = []
    with open(idfile) as f:
        ids = f.read().split('\n')[:use_no_files]
    #check if ids exist
    #ids = [myid for myid in ids if os.path.ispath(myid)]

    #remove .wav extension if it exists
    ids = [(myid[:-1*len(remove_extension)] if myid.endswith(remove_extension) else myid) for myid in ids]
    
    return ids

#mary = maryclient.maryclient()

#Rules for cleaning transcriptions, before using DFKI's TTS frontend MARY
pre_mary_transcription_replace_rules = {(u'º',u'°'),(u'“',u'"'), (u'„',u'"'),(u'‶',u'"')}
#Rules for cleaning transcriptions, after using DFKI's TTS frontend MARY
post_mary_transcription_replace_rules = {(u' x ', u' mal '),(u' k m ',u' kilometer '),(u' E U R ',u' Euro '),('O K ','okay '),(u'D i e ',u'Die '),(u'D a s ',u'Das '),(u'D e r ',u'Der '),(u'Philipp V ',u'Philipp den fünften ')}

def maryfySentence(sentence,mary,conn_num=0):
    ''' Use DFKI's MARY software to get a XML file which tokenizes and adds meta data to entities like numbers. We use it to convert e.g. "120" into "hundert twenty". Server has to run locally! Todo: inform user if it does not.'''

    for rule in pre_mary_transcription_replace_rules:
        target,replacement = rule
        sentence = sentence.replace(target,replacement)

    contents = mary.generate(sentence,conn_num)
    return contents

# Finds positions of ancronyms that MARY splits up in a list of tokens, e.x.
# For seq = ['Der','B','N','D','hat','beschloßen','nicht','mehr','mit','dem','C','I','A','...']
# This function yields: 
# [(1, 3), (10, 12)]

def find_mary_acronym(seq):
    for i,(elem,previous) in enumerate(zip(seq+['nil'],['nil']+seq+['nil'])):
        if len(elem)==1 and len(previous)>1:
            start = i
        elif len(previous)==1 and len(elem)>1:
            yield(start,i)

def collapseTokenSeqAt(seq,positions):
    offset = 0
    for start,end in positions:
        start -= offset
        end -= offset
        seq = cutSequenceWith(seq, ''.join(seq[start:end]), start, end)
        offset += (end - start - 1)
    return seq

def cutSequenceWith(seq, replace, start, end):
    '''cuts items at start until end from the list and replace it with one element'''
    assert(start >= 0 and start < len(seq))
    assert(end > start and end <= len(seq))
    return seq[:start] + [replace] + seq[end:]

def getCleanTokensAndPhonemes(sentence, mary, conn_num=0):
    '''This uses mary client (needs a working MARY server on localhost) to parse a raw sentence and return a sequence of tokens and a sequence of phonemes'''
    maryxml = maryfySentence(sentence,mary,conn_num)
    soup = BeautifulSoup(maryxml)

    tokens_with_meta = []

    for token in soup.find_all('t'):
        tokens_with_meta.append((unicode(token.string).strip(),token.attrs))

    #Filter punctuation and other unpronounceable stuff (todo: we should include an option to pronounce punctuation or leave it in there)
    tokens_with_meta = [elem for elem in tokens_with_meta if 'ph' in elem[1]]
    tokens_with_meta = [(token,meta) if not 'sounds_like' in meta else (meta['sounds_like'],meta) for (token,meta) in tokens_with_meta]

    tokens = [token for (token,meta) in tokens_with_meta]
    phonemes = [meta['ph'].replace(' ','') for (token,meta) in tokens_with_meta]

    # Try the sentence 'Die ARD hat berichtet...' with MARY; it returns separate tokens A R D for ARD. The following code replaces these separate one char length tokens by collapsign them to a single token
    replace_positions = list(find_mary_acronym(tokens))

    if len(replace_positions)>0:
        tokens = collapseTokenSeqAt(tokens,replace_positions)
        phonemes = collapseTokenSeqAt(phonemes,replace_positions)

    assert(len(tokens)==len(phonemes))

    return tokens,phonemes

#checks if a directory exists and create it if necessary, see http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
