# -*- coding: utf-8 -*-

# Copyright 2019 Language Technology, Universitaet Hamburg (author: Benjamin Milde)
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
import normalize_sentences
import spacy
import re

validated_filename = 'validated.tsv'

wav_scp_template = "sox $filepath -t wav -r 16k -b 16 -e signed - |"

def process(corpus_path, output_datadir):
    common_utils.make_sure_path_exists(output_datadir)
    nlp = spacy.load('de')

    # Common voice has repetitions and the text is not normalized
    # we cache text normalizations since they can be slow
    normalize_cache = {}

    # we first load the entire corpus text into memory, sort by ID and then write it out into Kaldis data_dir format
    corpus = {}

    print('Loading', corpus_path + validated_filename)
    with open(corpus_path + validated_filename) as corpus_path_in:
        for line in corpus_path_in:
            split = line.split('\t')
    #        print(split)

            #myid = split[0] 
            filename = split[1]
            text = split[2]
           
     #       print(filename)
            m = re.match(r'[^0-9]*([0-9]+)[^0-9]*mp3', filename)

            # only proceed if we can parse the sequence num from the filename
            if m:
                seq_num = int(m.group(1))

                myid = "%.10d" % seq_num 

                spk = myid

                if text not in normalize_cache:
                    normalized_text = normalize_sentences.normalize(nlp, text)
                    normalize_cache[text] = normalized_text
                else:
                    normalized_text = normalize_cache[text]

                #print(myid, filename, text, normalized_text)

                corpus[myid] = (filename, normalized_text)

    print('done loading common voice tsv!')
    print('Now writing out to', output_datadir,'in Kaldi format!')

    with open(output_datadir + 'wav.scp', 'w') as wav_scp, open(output_datadir + 'utt2spk', 'w') as utt2spk, open(output_datadir + 'text', 'w') as text_out:
        for myid in sorted(corpus.keys()):
            spk = myid
            fullid = spk + '_' + myid
            filename, normalized_text = corpus[myid]

            wav_scp.write(fullid + ' ' + wav_scp_template.replace("$filepath", corpus_path + 'clips/' + filename) + '\n')
            utt2spk.write(fullid + ' ' + spk + '\n')
            text_out.write(fullid + ' ' + normalized_text + '\n')

    print('done!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the Commonvoice German corpus for KALDI')
    parser.add_argument('-c', '--corpus-path', dest='corpus_path', help='path to the corpus data', default='data/wav/cv/', type=str)
    parser.add_argument('-o', '--output-datadir', dest='output_datadir', help='lexicon out file', type=str, default='data/commonvoice_train/')

    args = parser.parse_args()

    process(args.corpus_path, args.output_datadir)
