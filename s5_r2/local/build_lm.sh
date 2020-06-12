# Copyright 2014 (?) todo: research from which script this has been adapted from 
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
set -e # fail on error

srcdir=data/local/lang
dir=data/local/lm
lmstage=0

. ./utils/parse_options.sh

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

export LC_ALL=C

#train_lm.sh

mkdir -p $dir || true

. ./path.sh || exit 1; # for KALDI_ROOT
export PATH=$KALDI_ROOT/tools/kaldi_lm:$PATH

( # First make sure the kaldi_lm toolkit is installed.
 cd $KALDI_ROOT/tools || exit 1;
 if [ -d kaldi_lm ]; then
   echo Not installing the kaldi_lm toolkit since it is already there.
 else
   echo Downloading and installing the kaldi_lm tools
   if [ ! -f kaldi_lm.tar.gz ]; then
     wget http://www.danielpovey.com/files/kaldi/kaldi_lm.tar.gz || exit 1;
   fi
   tar -xvzf kaldi_lm.tar.gz || exit 1;
   cd kaldi_lm
   make || exit 1;
   echo Done making the kaldi_lm tools
 fi
) || exit 1;

#Get a wordlist-- keep everything but silence, which should not appear in
# the LM.
awk '{print $1}' $srcdir/lexiconp.txt | grep -v -w '!SIL' > $dir/wordlist.txt

if [ $lmstage -le 1 ]; then
	# Get training data with OOV words (w.r.t. our current vocab) replaced with  <UNK>
	echo "Getting training data with OOV words replaced with <UNK> (unkown word) (train_nounk.gz)"
	gunzip -c $dir/cleaned.gz | awk -v w=$dir/wordlist.txt \
	  'BEGIN{while((getline<w)>0) v[$1]=1;}
	  {for (i=1;i<=NF;i++) if ($i in v) printf $i" ";else printf "<UNK> ";print ""}'|sed 's/ $//g' \
	  | gzip -c > $dir/train_nounk.gz

	# Get unigram counts (without bos/eos, but this doens't matter here, it's
	# only to get the word-map, which treats them specially & doesn't need their
	# counts).
	# Add a 1-count for each word in word-list by including that in the data,
	# so all words appear.
	gunzip -c $dir/train_nounk.gz | cat - $dir/wordlist.txt | \
	  awk '{ for(x=1;x<=NF;x++) count[$x]++; } END{for(w in count){print count[w], w;}}' | \
	 sort -nr > $dir/unigram.counts

	# Get "mapped" words-- a character encoding of the words that makes the common words very short.
	cat $dir/unigram.counts  | awk '{print $2}' | get_word_map.pl "<s>" "</s>" "<UNK>" > $dir/word_map

	gunzip -c $dir/train_nounk.gz | awk -v wmap=$dir/word_map 'BEGIN{while((getline<wmap)>0)map[$1]=$2;}
	  { for(n=1;n<=NF;n++) { printf map[$n]; if(n<NF){ printf " "; } else { print ""; }}}' | gzip -c >$dir/train.gz

	echo training kaldi_lm with 3gram-mincount

	rm -r data/local/lm/3gram-mincount/ || true
	train_lm.sh --arpa --lmtype 3gram-mincount $dir
	train_lm.sh --arpa --lmtype 4gram-mincount $dir
fi

if [ $lmstage -le 2 ]; then
	prune_lm.sh --arpa 20.0 $dir/3gram-mincount/
	prune_lm.sh --arpa 30.0 $dir/3gram-mincount/

	prune_lm.sh --arpa 20.0 $dir/4gram-mincount/
	prune_lm.sh --arpa 30.0 $dir/4gram-mincount/
fi

# create unpruned const arpa for best path rescoring
# utils/build_const_arpa_lm.sh data/local/lm/3gram-mincount/lm_unpruned.gz data/lang/ data/lang_const_arpa/

echo done
exit 0
