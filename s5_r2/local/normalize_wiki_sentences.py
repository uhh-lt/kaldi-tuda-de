# -*- coding: utf-8 -*-

# Copyright 2019 Language Technology, Universität Hamburg (author: Benjamin Milde)
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


import sys
from bz2 import BZ2File as bzopen

import spacy
import json
import normalisierung

nlp = spacy.load('de_core_news_sm')

disable_pipeline = False
filter_exlude_zeichen = True
filter_satzzeichen = True
resplit_whitespace = True

if disable_pipeline:
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

if len(sys.argv) != 3:
    print('first argument must be the filename to process, second the output file')

filename = str(sys.argv[1])
filename_out = str(sys.argv[2])

min_token_len = 1

satzzeichen = ',.?!:;<>()/\{}#"\'´`‚’‘_→[]-~«»'

exlude_zeichen = '*/=→[]."'

sen_num = 0
lines_dropped = 0

with bzopen(filename) as bzin, open(filename_out, 'w') as txt_out:
    for line in bzin:
        try:
            line = line.decode('utf-8')
    #        print(line)
            #if("<doc" in line or "</doc>" in line):
            #    continue
            try:
                line_json = json.loads(line)

                text = line_json['text'] #.replace('\n','')
            except:
                text = line

            text = text.replace('\t',' ')
            text = text.replace('\xa0',' ')

            if resplit_whitespace:
                text = ' '.join(text.split())

            text = text.replace('   ', ' ').replace('  ', ' ')

            if disable_pipeline:
                text_sentences = nlp(text, disable=["tagger", "parser", "ner", "lemmatizer", "tokenizer"])        
            else:
                text_sentences = nlp(text)

            for sentence in text_sentences.sents:
                normalized_sentence = normalisierung.text_normalization(sentence.text, tries=8)
                
                if "<nowiki>" in line:
                    lines_dropped += 1
                    continue

                #if disable_pipeline:
                #    text_tokens = nlp(normalized_sentence, disable=["parser", "sentencizer", "lemmatizer"])
                #else:
                #    text_tokens = nlp(normalized_sentence)

                text_tokens = nlp(normalized_sentence, disable=["parser", "sentencizer", "lemmatizer"])

                # NE PROPN       proper noun
                # NNE PROPN       proper noun
                # NN  NOUN        noun, singular or mass
                
                lower_case_first = False

             #   print(text_tokens[0].tag_)

                if len(text_tokens) == 0:
                    lines_dropped += 1
                    continue

                try:
                    if text_tokens[0].tag_ not in ["NE", "NNE", "NN"]:
                        lower_case_first = True
                except:
                    print("Warning could not retrieve tag!")

                if filter_satzzeichen:
                    tokens = [token.text for token in text_tokens if token.text not in satzzeichen] #if (token.text != '\n' and token.text != ' ')]
                    tokens = [token[:-1] if token[-1] == '-' else token for token in tokens]
                    tokens = [token[1:] if token[0] == '-' else token for token in tokens]
                else:
                    tokens = [token.text for token in text_tokens]

                if len(tokens) < min_token_len:
                    lines_dropped += 1
                    continue

                rejoined_text = ' '.join(tokens).strip()

                if filter_exlude_zeichen and any(character in exlude_zeichen for character in rejoined_text):
                    lines_dropped += 1
                    continue

                while '  ' in rejoined_text:
                    rejoined_text = rejoined_text.replace('  ',' ')
                
                if rejoined_text == '':
                    lines_dropped += 1
                    continue

                if lower_case_first:
                    rejoined_text = rejoined_text[0].lower() + rejoined_text[1:]

                if sen_num % 1000 == 0:
                    print("At sentence:", sen_num)
                    print(tokens)

                if rejoined_text != '' and rejoined_text != ' ' and ('.' not in rejoined_text or not filter_satzzeichen):
                    txt_out.write(rejoined_text.replace(' \n','\n').replace('\n ','\n') + '\n')

                sen_num += 1

                #print(normalized_sentence)
                #nlp(normalized_sentence)
                #tokens = [word.text for word in sentence]
                #print(tokens)
        except:
            print("Error, skipping line")

print("Finished processing " + str(sen_num) + " sentences.")
print("Dropped " + str(lines_dropped) + " sentences.")
