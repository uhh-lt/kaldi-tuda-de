#!/bin/bash

#adapted from gale_arabic run.sh

use_BAS_dictionaries=false
sequitur_g2p="/home/me/comp/g2p/g2p.py"

if [ -f $sequitur_g2p ]
then
    echo "Using $sequitur_g2p for g2p conversion of OOV words."
else
    echo "Could not find g2p.py"
    echo "Please edit run.sh and point sequitur_g2p to the g2p.py python script of your Sequitur G2P installation."
    echo "Sequitur G2P can be downloaded from https://www-i6.informatik.rwth-aachen.de/web/Software/g2p.html"
    echo "E.g. wget https://www-i6.informatik.rwth-aachen.de/web/Software/g2p-r1668-r3.tar.gz"
    exit
fi

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
python3 local/prepare_dir_structure.py

if [ ! -d data/wav/german-speechdata-package-v2 ]
then
    wget --directory-prefix=data/wav/ http://speech.tools/kaldi_tuda_de/german-speechdata-package-v2.tar.gz
    cd data/wav/
    tar xvfz german-speechdata-package-v2.tar.gz
    cd ../../
fi

#adapt this to the Sprachdatenaufnahmen2014 folder on your disk
RAWDATA=data/wav/german-speechdata-package-v2

# Filter by name
FILTERBYNAME="*.xml"

find $RAWDATA/*/$FILTERBYNAME -type f > data/waveIDs.txt
#python local/data_prepare.py -f data/waveIDs.txt
python3 local/data_prepare.py -f data/waveIDs.txt

# Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    # this lexicon is licensed under LGPL
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts-lexicon-de/master/modules/de/lexicon/de.txt
#    echo "data/lexicon/train.txt">> data/lexicon_ids.txt
    echo "data/lexicon/de.txt">> data/lexicon_ids.txt
fi

if [ use_BAS_dictionaries = true ] ; then

  # These lexicons are publicly available on BAS servers, but can probably not be used in a commercial setting.
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
fi

#Transform freely available dictionaries into lexiconp.txt file + extra files 
mkdir -p data/local/dict/
python3 local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict 
python3 local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt 

g2p_model=data/local/g2p/de_g2p_model
final_g2p_model=${g2p_model}-6

if [ ! -f $final_g2p_model ]
then
    mkdir -p data/local/g2p/
    train_file=data/local/g2p/lexicon.txt
    
    cut -d" " -f 1,3- data/local/dict/lexiconp.txt > $train_file
    cut -d" " -f 1 data/local/dict/lexiconp.txt > data/local/g2p/lexicon_wordlist.txt

    $sequitur_g2p --train $train_file --devel 3% --write-model ${g2p_model}-1
    $sequitur_g2p --model ${g2p_model}-1 --ramp-up --train $train_file --devel 3% --write-model ${g2p_model}-2
    $sequitur_g2p --model ${g2p_model}-2 --ramp-up --train $train_file --devel 3% --write-model ${g2p_model}-3
    $sequitur_g2p --model ${g2p_model}-3 --ramp-up --train $train_file --devel 3% --write-model ${g2p_model}-4
    $sequitur_g2p --model ${g2p_model}-4 --ramp-up --train $train_file --devel 3% --write-model ${g2p_model}-5
    $sequitur_g2p --model ${g2p_model}-5 --ramp-up --train $train_file --devel 3% --write-model ${g2p_model}-6
else
    echo "G2P model file $final_g2p_model already exists, not recreating it."
fi

echo "Now finding OOV in train"
python3 local/find_oov.py -c data/train/text -w data/local/g2p/lexicon_wordlist.txt -o data/local/g2p/oov.txt

echo "Now using G2P to predict OOV"

exit

#Move old lang dir if it exists
mkdir -p data/lang/old
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
#sort data/local/dict/lexiconp.txt > data/local/dict/lexiconp.txt

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
    wget --directory-prefix=data/local/lm/ http://speech.tools/kaldi_tuda_de/German_sentences_8mil_filtered_maryfied.txt.gz
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

