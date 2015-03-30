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
import maryclient
import StringIO
import os

from bs4 import BeautifulSoup

from common_utils import make_sure_path_exists
import collections
import itertools

#Example xml file from the corpus:

#<?xml version="1.0" encoding="utf-8"?><Recording><rate>16000</rate><angle>-19,9962270500657</angle><gender>female</gender><ageclass>21-30</ageclass><sentence>Die Beute greifen die Adler meist auf dem Boden oder im bodennahen Luftraum und töten sie mit den außerordentlich kräftigen Zehen und Krallen.</sentence><corpus>wikipedia</corpus><muttersprachler>Ja</muttersprachler><bundesland>Mecklenburg-Vorpommern</bundesland></Recording>

#After this amount of seconds between utterance recordigs, decide that a new speaker is recording the utterance (simple heuristic,  unfortunately corpus doesnt contain this information) 
speakerid_diff_heuristic = 180

mary = maryclient.maryclient()

def exportDict(dest_file,utterances_phoneme_dict):
    with codecs.open(dest_file,'w','utf-8') as out:
        for word in utterances_phoneme_dict:
            out.write(word+' '+utterances_phoneme_dict[word]+'\n')

def writeKaldiDataFolder(dest_dir, utts, postfix, wavextension):
    ''' Exports the internal representation utts for all utterances into KALDIs corpus description format '''
    # Kaldi format, files: text,wav.scp,utt2spk,spk2gender

    # File: text
    # List of:
    # recording-id transcription

    # File: wav.scp
    # List of:
    # recording-id extended-filename

    # File: utt2spk
    # List of:
    # utteranceid speaker
    
    # File: spk2gender
    # List of:
    # speakerid gender

    #All files need to be sorted by key value!

    make_sure_path_exists(dest_dir)

    with open(dest_dir+'wav.scp','w') as wavscp, open(dest_dir+'utt2spk','w') as utt2spk, open(dest_dir+'spk2gender','w') as spk2gender, codecs.open(dest_dir+'text','w','utf-8') as text:
        speaker2gender = {}
        
        #sort by kaldi id
        utts = sorted(utts,key=lambda utt:utt['kaldi_id'])

        for utt in utts:
            kaldi_id = utt['kaldi_id']
            transcription = ' '.join(utt['clean_sentence_tokens'])

            for rule in common_utils.post_mary_transcription_replace_rules:
                target,replacement = rule
                transcription = transcription.replace(target,replacement)
            
            text.write(kaldi_id+' '+transcription+'\n')
            wavscp.write(kaldi_id+' '+utt['fileid']+postfix+wavextension+'\n')
            utt2spk.write(kaldi_id+' '+utt['speakerid']+'\n')
            speaker2gender[utt['speakerid']] = utt['gender']

        #sort by speaker
        speaker2gender = collections.OrderedDict(sorted(speaker2gender.items(), key=lambda x: x[0]))

        for speaker,gender in speaker2gender.iteritems():
            spk2gender.write(speaker+' '+('f' if gender=='female' else 'm')+'\n')

# Simple train test split that ignores speaker ids (dont use this one!)
def simpleTrainTestSplit(utts):
    train, test = [],[]
    for i,utt in enumerate(utts):
        if i%10==0:
            test.append(utt)
        else:
            train.append(utt)
    return train, test

#detect train/dev/test in the filenames of the ids. 
def filenameSplit(utts):
    train = [utt for utt in utts if 'train' in utt['fileid']]
    dev = [utt for utt in utts if 'dev' in utt['fileid']]
    test = [utt for utt in utts if 'test' in utt['fileid']]
    #sanity checks
    for utt in test:
        if utt in train:
            print 'WARNING overlapping test/train IDs. This is bad, check your filenaming scheme, no file should have both test and train in the name.'

    for utt in dev:
        if utt in train:
            print 'WARNING overlapping dev/train IDs. This is bad, check your filenaming scheme, no file should have both dev and train in the name.'
    return train, test, dev

# Extract date as best as possible from filename
def getDateFromID(myid):
    if '/' in myid:
        rawdate = myid.split('/')[-1]
    else:
        rawdate = myid

    split = rawdate.split('-')

    #some files prefix the corpus before the date, if thats the case irgnore first element
    if not split[0].isdigit():
        split = split[1:]

    #e.g. train/2014-05-13-10-15-35-

    date = datetime.datetime(int(split[0]),int(split[1]),int(split[2]),int(split[3]),int(split[4]),int(split[5]))
    return date


#This only makes sense when iterating over XML files, not used anymore
def filterRepeatUtterances(utts):
    old_utt = None
    filtered_utt = []
    for utt in reversed(utts):
        if old_utt != None:
            if utt['fileid'].count('repeat') >= old_utt['fileid'].count('repeat'):
                filtered_utt.append(utt)
            else:
                #We should have already encountered the sentence. Do a sanity check.
                if utt['sentence'] != old_utt['sentence']:
                    filtered_utt.append(utt)
                else:
                    print old_utt['sentence'], 'vs', utt['sentence']
                    print old_utt['fileid'], 'vs', utt['fileid']
        old_utt = utt
    return reversed(filtered_utt)

#find_sublists and replace_sublist from http://stackoverflow.com/questions/12898023/replacing-a-sublist-with-another-sublist-in-python
def find_sublists(seq, sublist):
    length = len(sublist)
    for index, value in enumerate(seq):
        if value == sublist[0] and seq[index:index+length] == sublist:
            yield index, index+length

def replace_sublist(seq, target, replacement):
    assert(target != replacement)
    sublists = find_sublists(seq, target)
    #if maxreplace:
    #    sublists = itertools.islice(sublists, maxreplace)
    for start, end in sublists:
        seq[start:end] = replacement
    return seq

#Load corpus xml files into python structures with BeautifulSoup
def getUtterances(ids, postfix_speaker ,cache_cleaned_sentences = True):
    '''Loads the corpus and gets python structured object that can be used to export the corpus to a format KALDI understands'''
    utts= []
    
    cleaned_sentences_cache = {}
    utts_phoneme_dict = {}

    print 'Reading corpus transcriptions and producing automatic corpus phoneme dict for OOV words (you need MARY running in the background!)'

    lastutt = None
    for myid in ids:
        print '.',
        #if 1==1:
        try:
            with codecs.open(myid+'.xml','r','utf-8') as myfile:
                #extract xml meta 
                xml = myfile.read()
                soup = BeautifulSoup(xml)
                sentence = soup.recording.sentence.string
                cleaned_sentence = soup.recording.cleaned_sentence.string
                gender = soup.recording.gender.string
                age = soup.recording.ageclass.string
                corpus = soup.recording.corpus.string
                nativespeaker = soup.recording.muttersprachler.string
                region = soup.recording.bundesland.string
                speakerid= soup.recording.speaker_id.string

                date = getDateFromID(myid)

                if cache_cleaned_sentences and (cleaned_sentence not in cleaned_sentences_cache):
                    clean_sentence_tokens,token_phonemes = common_utils.getCleanTokensAndPhonemes(cleaned_sentence,mary)
                    cleaned_sentences_cache[cleaned_sentence] = (clean_sentence_tokens,token_phonemes)
                    #print 'cleaning ', cleaned_sentence, ' -> ', clean_sentence_tokens , ' phonemes:', token_phonemes
                else:
                    clean_sentence_tokens,token_phonemes = cleaned_sentences_cache[cleaned_sentence]

                if not cache_cleaned_sentences:
                    clean_sentence_tokens,token_phonemes = common_utils.getCleanTokensAndPhonemes(sentence,mary)

                for token,phoneme_representation in itertools.izip(clean_sentence_tokens,token_phonemes):
                    if token not in utts_phoneme_dict:
                        utts_phoneme_dict[token] = phoneme_representation
                #old speaker id was: 's'+('%04d'%speakerid)
                utt = {'id':myid.split('/')[-1],'fileid':myid,'sentence':sentence,'clean_sentence_tokens':clean_sentence_tokens,'speakerid':speakerid,'gender':gender,'age':age,'corpus':corpus,'nativespeaker':nativespeaker,'region':region,'date':date}
                utts.append(utt)

        except Exception as err:
            print 'Error in file, omitting', myid
            print err

    #Sort utterances by date
    utts = sorted(utts,key=lambda utt:utt['date'])

    #Unfortunately, the xmls dont have speaker meta-information, we try to guess it here
    #for i,utt in enumerate(utts):
    #    if lastutt is not None:
    #        delta = utt['date'] - lastutt['date']
    #        diff = abs(delta.total_seconds())
    #        #Heuristic: either a enough time passed between this and the last recording, or speaker meta information (gender,age,region) changed
    #        if diff > speakerid_diff_heuristic or lastutt['gender'] != utt['gender'] or lastutt['age'] != utt['age'] or lastutt['region'] != utt['region']:
    #            print 'probable new speaker',speakerid
    #            if diff > speakerid_diff_heuristic:
    #                print 'based on time diff',diff
    #            else:
    #                print 'based on meta', 'diff:',diff, lastutt['gender'],utt['gender'],lastutt['age'],utt['age'],lastutt['region'],utt['region']
    #            speakerid += 1
    #    utt['speakerid'] = 's'+('%04d'%speakerid)+postfix_speaker
        
    for utt in utts:    
        utt['kaldi_id'] = utt['speakerid']+'_'+utt['id']
        
        #utts[i] = utt
        
        #lastutt = utt

    #Filter utterances with repeat in file name (recording was repeated after a wrong utterance)
    #utts = filterRepeatUtterances(utts)

    return utts,utts_phoneme_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the TUDA corpus (XML) into text transcriptions for KALDI')
    parser.add_argument('-f', '--filelist', dest='filelist', help='process this file list', type=str, default = '')
    parser.add_argument('-r', '--remove_extension', dest='remove_extension', help='remove this extension, to get plain file id', type=str, default='.xml')
    parser.add_argument('-w', '--audio-file-extension', dest='wav_extension', help='extension for audio files', type=str, default='.wav')
    parser.add_argument('-p', '--utterance-postfix-name', dest='postfix', help='--utterance-postfix-name', type=str, default='-beamformedSignal')

    args = parser.parse_args()

    if args.filelist == '':
        print 'Corpus filelist is empty. Use -f to supply a filelist!'
    else:

        print 'Load ', args.filelist, ', ommit ', args.remove_extension

        ids_raw = common_utils.loadIdFile(args.filelist,remove_extension=args.remove_extension)
        print 'I have',len(ids_raw),'files. Some may have their audio missing, I\'ll check that for you...'
        ids = []
        #check for missing wav files:
        
        for myid in ids_raw:
            check = myid+args.postfix+args.wav_extension
            if os.path.isfile(check):
                ids.append(myid)
            else:
                print 'Warning, omitting',myid,'because I can\'t find',check
        
        print 'Found',len(ids),'files.'

        utterances,utterances_phoneme_dict = getUtterances(ids,args.postfix)
        
        print 'Done. Some example utterances:'
        
        for utt in utterances[:10]:
            print utt['sentence'].encode('utf-8'),utt
            #print utt.sentence,utt.speakerid,utt.gender,utt.age,utt.corpus,utt.nativespeaker,utt.region,utt.date

        print 'Export to kaldi train/test dirs...'

        #train, test = simpleTrainTestSplit(utterances)
        train, test, dev = filenameSplit(utterances)
    
        writeKaldiDataFolder('data/train/', train,args.postfix, args.wav_extension)
        writeKaldiDataFolder('data/dev/', dev, args.postfix, args.wav_extension)
        writeKaldiDataFolder('data/test/', test, args.postfix, args.wav_extension)
        writeKaldiDataFolder('data/all/', utterances, args.postfix, args.wav_extension)

        exportDict('data/lexicon/train.txt',utterances_phoneme_dict)

        print 'Done!'
