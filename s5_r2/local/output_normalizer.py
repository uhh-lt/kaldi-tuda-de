# -*- coding: utf-8 -*-

# Copyright 2022 Language Technology and HiTEC e.V., Universität Hamburg (author: Benjamin Milde)
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

import sys
import argparse

from german_asr_lm_tools.normalize_numbers import NumberFormatter

# Also change some very frequent words to new ortographic rules in German
# e.g. muß -> muss
word_replace_rules = {'muß':'muss', 'daß':'dass', 'Daß':'dass', '-$':' ', '-$':' ', '$':'', '$':'', '-':'' , '  ' : ' '}

def process_input(norm_number_words=False, convert_numbers=False):
    if norm_number_words or convert_numbers:
        nf = NumberFormatter()

    for line in sys.stdin:
        line = line.replace('Das', 'das')
        # remove ähs, ähms and unks as well as hesitations (häs)
        line = line.replace('Äh', '').replace('äh', '').replace('Ähm', '').replace('ähm', '').replace('häs', '').replace('<UNK>', '').replace('<unk>', '')
        split = line.split()
        if norm_number_words or convert_numbers:
             split = nf.normalize_text(split, convert_to_numbers=convert_numbers)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the TUDA corpus (XML) into text transcriptions for KALDI')
    #parser.add_argument('-f', '--file', dest='file', help='process this (python pickle) lexicon file', type=str)
    parser.add_argument('-w', '--norm-number-words', dest='norm_number_words', help='Normalize number words (drei und sechzig -> dreiundsechzig)', action='store_true', default=False)
    parser.add_argument('-n', '--convert-numbers', dest='convert_numbers', help='Convert numbers (drei und sechzig -> 63, dreiundsechzig -> 63)', action='store_true', default=False)

    args = parser.parse_args()
    process_input(args.norm_number_words, args.convert_numbers)
