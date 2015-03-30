#!/bin/bash

# Adapted from gale_arabic scripts

# Copyright 2015 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
# Copyright 2014 QCRI (author: Ahmed Ali)
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

if [ -f cmd.sh ]; then
    . cmd.sh; else
    echo "missing cmd.sh"; exit 1;
fi

if [ -f path.sh ]; then
  . path.sh; else
   echo "missing path.sh"; exit 1;
fi 

export LC_ALL=C

#for dir in test train; do 
#   cp -pr data/local/$dir data/$dir
#done

mkdir -p data/lang_test

arpa_lm=data/local/lm/3gram-mincount/lm_pr6.0.gz
[ ! -f $arpa_lm ] && echo No such file $arpa_lm && exit 1;

rm -r data/lang_test
cp -r data/lang data/lang_test

# grep -v '<s> <s>' etc. is only for future-proofing this script.  Our
# LM doesn't have these "invalid combinations".  These can cause 
# determinization failures of CLG [ends up being epsilon cycles].
# Note: remove_oovs.pl takes a list of words in the LM that aren't in
# our word list.  Since our LM doesn't have any, we just give it
# /dev/null [we leave it in the script to show how you'd do it].
gunzip -c "$arpa_lm" | \
   grep -v '<s> <s>' | \
   grep -v '</s> <s>' | \
   grep -v '</s> </s>' | \
   arpa2fst - | fstprint | \
   utils/remove_oovs.pl /dev/null | \
   utils/eps2disambig.pl | utils/s2eps.pl | fstcompile --isymbols=data/lang_test/words.txt \
     --osymbols=data/lang_test/words.txt  --keep_isymbols=false --keep_osymbols=false | \
    fstrmepsilon | fstarcsort --sort_type=ilabel > data/lang_test/G.fst
  fstisstochastic data/lang_test/G.fst

exit 0;

#rest of this script is sanity checks, which are currently disabled

echo  "Checking how stochastic G is (the first of these numbers should be small):"
fstisstochastic data/lang_test/G.fst 

## Check lexicon.
## just have a look and make sure it seems sane.
echo "First few lines of lexicon FST:"
fstprint   --isymbols=data/lang/phones.txt --osymbols=data/lang/words.txt data/lang/L.fst  | head

echo Performing further checks

# Checking that G.fst is determinizable.
fstdeterminize data/lang_test/G.fst /dev/null || echo Error determinizing G.

# Checking that L_disambig.fst is determinizable.
fstdeterminize data/lang_test/L_disambig.fst /dev/null || echo Error determinizing L.

# Checking that disambiguated lexicon times G is determinizable
# Note: we do this with fstdeterminizestar not fstdeterminize, as
# fstdeterminize was taking forever (presumbaly relates to a bug
# in this version of OpenFst that makes determinization slow for
# some case).
fsttablecompose data/lang_test/L_disambig.fst data/lang_test/G.fst | \
   fstdeterminizestar >/dev/null || echo Error

# Checking that LG is stochastic:
fsttablecompose data/lang/L_disambig.fst data/lang_test/G.fst | \
   fstisstochastic || echo LG is not stochastic

echo format_data sanity checks succeeded.
