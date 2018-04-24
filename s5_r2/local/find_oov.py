# -*- coding: utf-8 -*-

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

from __future__ import print_function


import io
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finds out of vocabulary (OOV) words in a Kaldi text transcription file given a wordlist.')
    parser.add_argument('-c', '--corpus-text', dest='corpustext', help='process this Kali format transcription text file', type=str, default='data/train/text')
    parser.add_argument('-w', '--wordlist', dest='wordlist', help='this is the current wordlist', type=str, default='wordlist.txt')
    parser.add_argument('-o', '--outfile', dest='outfile', help='write OOV words to this file', type=str, default='oov.txt')
#    parser.add_argument('-sph', '--sphinx-format', dest='sphinx_format', help='export lexicon in sphinx format', action='store_true', default=False)

    train_words = {}
    oov_words = {}

    args = parser.parse_args()

    with io.open(args.wordlist,'r',encoding='utf-8') as infile:
        for line in infile:
            if line[-1] == '\n':
                line = line[:-1]
            word = line
            if word not in train_words:
                train_words[word] = True

    with io.open(args.corpustext,'r',encoding='utf-8') as infile:
        for line in infile:
            split = line.split()[1:]
            for word in split:
                if word not in train_words:
                    if word not in oov_words:
                        oov_words[word] = True

    with io.open(args.outfile,'w',encoding='utf-8') as outfile:
        for word in sorted(list(oov_words.keys())):
            outfile.write(word + '\n')

