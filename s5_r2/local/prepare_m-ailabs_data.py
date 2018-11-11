#!/usr/bin/env python3

# Copyright 2018 Pavel Denisov
# Copyright 2018 Language Technology, Universitaet Hamburg (author: Benjamin Milde)
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
import sys
import glob
import json
import re
import subprocess
import argparse
import common_utils

punct = re.compile('[ !\',\-\.:;\?]+')

def create_kaldi_datadir(odir, mailabs_corpus_dir):
    with open(odir + '/text', 'w', encoding='utf-8') as text, \
        open(odir + '/wav.scp', 'w') as wavscp, \
        open(odir + '/utt2spk', 'w') as utt2spk:

        for annotation in glob.glob(mailabs_corpus_dir + '/by_book/**/metadata_mls.json', recursive=True):
            utts = {}

            with open(annotation) as a:
                utts = json.load(a)

            wavdir = annotation[:annotation.rindex('/')] + '/wavs/'
            spk = annotation.split('/')[-3]

            for wav in utts:
                if spk == 'mix':
                    wspk = 'm-ailabs-' + wav[:-4]
                else:
                    wspk = 'm-ailabs-' + spk

                uttid = wspk + '_' + wav[:-4]

                text.write('{} {}\n'.format(uttid, re.sub(punct, ' ', utts[wav]['clean']).strip()))
                utt2spk.write('{} {}\n'.format(uttid, wspk))
                wavscp.write('{} sox {} -r 16k -t wav -c 1 -b 16 -e signed - |\n'.format(uttid, wavdir + wav))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepares the German data from the M-ailabs corpus (http://www.m-ailabs.bayern/en/the-mailabs-speech-dataset/) for Kaldi.')
    parser.add_argument('-i', '--inputcorpus', dest='inputcorpus',
                        help='Path to the M-ailabs data (download here: http://www.m-ailabs.bayern/en/the-mailabs-speech-dataset/)', type=str, default='data/wav/m_ailabs/de_DE/')
    parser.add_argument('-o', '--outputfolder', dest='outputfolder',
                        help='Export to this Kaldi folder.', type=str, default='data/m_ailabs_train')
    args = parser.parse_args()

    common_utils.make_sure_path_exists(args.outputfolder)

    create_kaldi_datadir(args.outputfolder, args.inputcorpus)

    #subprocess.call('utils/fix_data_dir.sh {}'.format(odir), shell=True)
