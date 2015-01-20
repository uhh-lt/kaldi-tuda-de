#!/bin/bash

#adapted from gale_arabic run.sh

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

RAWDATA=/srv/data/Sprachdatenaufnahmen2014

# mfccdir should be some place with a largish disk where you
# want to store MFCC features.
mfccdir=mfcc

# Filter by name
FILTERBYNAME="*-kinect-.wav"

find $RAWDATA/$FILTERBYNAME -type f > data/waveIDs.txt
python local/data_prepare.py -f data/waveIDs.txt -r="-kinect-.wav"

python local/prepare_dir_structure.py

#Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt 
fi

if [ ! -f data/lexicon/VM.German.Wordforms ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/VM.German.Wordforms
fi

if [ ! -f data/lexicon/RVG1_read.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_read.lex
fi

if [ ! -f data/lexicon/RVG1_trl.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_trl.lex
fi

if [ ! -f data/lexicon/LEXICON.TBL ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG-J/LEXICON.TBL
fi

#Transform freely available dictionaries into lexiconp.txt file + extra files 
mkdir -p data/local/dict/
python local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict 
python local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt 

#Move old lang dir if it exists
mv data/lang data/lang_old

#Prepare phoneme data for Kaldi
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

# Now make MFCC features.
for x in train test ; do
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs \
    data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
done

#Todo: download source sentence archive for LM building

#Prepare ARPA LM
local/build_lm.sh

#Transform LM into Kaldi LM format 
local/format_data.sh

# Here we start the AM

# Let's create a subset with 10k segments to make quick flat-start training:
# utils/subset_data_dir.sh data/train 10000 data/train.10K || exit 1;

local/run_am.sh
local/run_dnn.sh

