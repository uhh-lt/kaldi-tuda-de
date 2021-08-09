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
import shutil
import time

def load_lowercase_stopwords(filename='local/stopwords.de.txt'):
    stopwords = {}
    with open(filename) as stopwords_in:
        for line in stopwords_in:
            if line[-1] == '\n':
                line = line[:-1]
            if line.startswith('#'):
                continue
            stopwords[line] = True

    return stopwords

def process(text_kaldi_file):
    nlp = spacy.load('de_core_news_sm')
    texts = []
    normalize_cache = {}
    i=0

    nonce = str(int(time.time()))
    print('Making a backup of the original file:', text_kaldi_file, '=>', text_kaldi_file + '.orig' + nonce)
    shutil.copyfile(text_kaldi_file, text_kaldi_file + '.orig' + nonce)

    stopwords = load_lowercase_stopwords()

    print('Opening and processing', text_kaldi_file)
    with open(text_kaldi_file) as infile:
        for line in infile:
            i +=1

            if i%10000 == 0:
                print('At line:', i)

            if line[-1] == '\n':
                line = line[:-1]
            split = line.split()

            # first element in the split id the ID
            if len(split) > 1:
                myid = split[0]
                text = ' '.join(split[1:])

                first_word = split[1]

                if text not in normalize_cache:
                    should_lowercase = first_word in stopwords

                    try:
                        normalized_text = normalize_sentences.normalize(nlp, text)
                        # Npte the normalization step looks at POS tags to decide if the first word should be lowercased, but gets some 
                        if should_lowercase:
                            # check that the first word isnt in all upper case:
                            if not normalized_text[1].isupper():
                                normalized_text = normalized_text[0].lower() + normalized_text[1:]
                        normalize_cache[text] = normalized_text
                    except:
                        print('Warning, error normalizing:', text)
                        continue
                else:
                    normalized_text = normalize_cache[text]

                texts.append(myid + ' ' + normalized_text)
            else:
                print('Warning,', myid, 'has no text!')

    print('Rewrite', text_kaldi_file)
    with open(text_kaldi_file, 'w') as outfile:
        outfile.write('\n'.join(texts))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Renormalize text file in Kaldi data dir format.')
    parser.add_argument('-t', '--text-kaldi-file', dest='text_kaldi_file', help='path to the Kaldi text file',  type=str)

    args = parser.parse_args()

    process(args.text_kaldi_file)
