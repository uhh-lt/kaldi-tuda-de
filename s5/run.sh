#!/bin/bash

#adapted from gale_arabic run.sh

[ ! -L "steps" ] && ln -s ../../wsj/s5/steps

[ ! -L "utils" ] && ln -s ../../wsj/s5/utils

# mfccdir should be some place with a largish disk where you
# want to store MFCC features.
mfccdir=mfcc

utf8()
{
    iconv -f ISO-8859-1 -t UTF-8 $1 > $1.tmp
    mv $1.tmp $1
}

# Prepares KALDI dir structure and asks you where to store mfcc vectors and the final models (both can take up significant space)
python local/prepare_dir_structure.py

if [ ! -d data/wav/german-speechdata-package-v2 ]
then
    wget --directory-prefix=data/wav/ http://dialogplus.lt.informatik.tu-darmstadt.de/downloads/speechdata/german-speechdata-package-v2.tar.gz
    cd data/wav/
    tar xvfz german-speechdata-package-v2.tar.gz
    cd ../../
fi

#adapt this to the Sprachdatenaufnahmen2014 folder on your disk
RAWDATA=data/wav/german-speechdata-package-v2

# Filter by name
FILTERBYNAME="*.xml"

find $RAWDATA/*/$FILTERBYNAME -type f > data/waveIDs.txt
python local/data_prepare.py -f data/waveIDs.txt

# Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt 
    echo "data/lexicon/train.txt">> data/lexicon_ids.txt
    echo "data/lexicon/de.txt">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/VM.German.Wordforms ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/VM.German.Wordforms
    echo "data/lexicon/VM.German.Wordforms">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/RVG1_read.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_read.lex
    echo "data/lexicon/RVG1_read.lex">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/RVG1_trl.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_trl.lex
    echo "data/lexicon/RVG1_trl.lex">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/LEXICON.TBL ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG-J/LEXICON.TBL
    utf8 data/lexicon/LEXICON.TBL
    echo "data/lexicon/LEXICON.TBL">> data/lexicon_ids.txt
fi


#Transform freely available dictionaries into lexiconp.txt file + extra files 
mkdir -p data/local/dict/
python local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict 
python local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt 

#Move old lang dir if it exists
mkdir data/lang/old
mv data/lang/* data/lang/old

#Now start preprocessing with KALDI scripts

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

#Path also sets LC_ALL=C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs. It should be set here, after the python scripts and not at the beginning of this script
if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;

fi

echo "Runtime configuration is: nJobs $nJobs, nDecodeJobs $nDecodeJobs. If this is not what you want, edit cmd.sh!"

#Make sure that LC_ALL is C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs
export LC_ALL=C

#Sort the lexicon with C-encoding (Is this still needed?)
sort data/local/dict/lexiconp.txt > data/local/dict/lexiconp.txt

#Prepare phoneme data for Kaldi
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

# Now make MFCC features.
for x in train dev test ; do
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x
done

#Todo: download source sentence archive for LM building

mkdir -p data/local/lm/

if [ ! -f data/local/lm/cleaned.gz ]
then
    wget --directory-prefix=data/local/lm/ http://dialogplus.lt.informatik.tu-darmstadt.de/downloads/speechdata/German_sentences_8mil_filtered_maryfied.txt.gz
    mv data/local/lm/German_sentences_8mil_filtered_maryfied.txt.gz data/local/lm/cleaned.gz
fi

#Prepare ARPA LM

#If you wont to build your own:
local/build_lm.sh

#Otherwise you can also use the supplied LM:
#wget speechdata-LM.arpa

#Transform LM into Kaldi LM format 
local/format_data.sh

# Here we start the AM

# Let's create a subset with 10k segments to make quick flat-start training:
# utils/subset_data_dir.sh data/train 10000 data/train.10K || exit 1;

local/run_am.sh
#local/run_dnn.sh

