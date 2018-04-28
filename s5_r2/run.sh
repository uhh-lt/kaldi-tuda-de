#!/bin/bash

#adapted from swbd Kaldi run.sh

stage=10
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

if [ $stage -le 1 ]; then
  # Prepares KALDI dir structure and asks you where to store mfcc vectors and the final models (both can take up significant space)
  python3 local/prepare_dir_structure.py

  if [ ! -d data/wav/german-speechdata-package-v2 ]
  then
      wget --directory-prefix=data/wav/ http://speech.tools/kaldi_tuda_de/german-speechdata-package-v2.tar.gz
      cd data/wav/
      tar xvfz german-speechdata-package-v2.tar.gz
      cd ../../
  fi
fi

#adapt this to the Sprachdatenaufnahmen2014 folder on your disk
RAWDATA=data/wav/german-speechdata-package-v2

# Filter by name
FILTERBYNAME="*.xml"

if [ $stage -le 2 ]; then
  find $RAWDATA/*/$FILTERBYNAME -type f > data/waveIDs.txt
  #python local/data_prepare.py -f data/waveIDs.txt
  python3 local/data_prepare.py -f data/waveIDs.txt
fi

if [ $stage -le 3 ]; then
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
fi

if [ $stage -le 3 ]; then
  #Transform freely available dictionaries into lexiconp.txt file + extra files 
  mkdir -p data/local/dict/
  python3 local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict 
  python3 local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/_lexiconp.txt 
fi

g2p_model=data/local/g2p/de_g2p_model
final_g2p_model=${g2p_model}-6

if [ $stage -le 4 ]; then
  if [ ! -f $final_g2p_model ]
  then
      mkdir -p data/local/g2p/
      train_file=data/local/g2p/lexicon.txt
      
      cut -d" " -f 1,3- data/local/dict/_lexiconp.txt > $train_file
      cut -d" " -f 1 data/local/dict/_lexiconp.txt > data/local/g2p/lexicon_wordlist.txt

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
  $sequitur_g2p  --model $final_g2p_model --apply data/local/g2p/oov.txt > data/local/dict/oov_lexicon.txt
  cat data/local/dict/oov_lexicon.txt | awk '{$1=$1" 1.0"; print }' > data/local/dict/oov_lexiconp.txt
  #data/local/dict/oov_lexicon.txt
  echo "Done!"
fi

# Now start preprocessing with KALDI scripts

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

# Path also sets LC_ALL=C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs. It should be set here, after the python scripts and not at the beginning of this script
if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;

fi

echo "Runtime configuration is: nJobs $nJobs, nDecodeJobs $nDecodeJobs. If this is not what you want, edit cmd.sh!"

# Make sure that LC_ALL is C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs
# We set it here, because the Python data preparation scripts need a propoer utf local in LC_ALL
export LC_ALL=C

if [ $stage -le 5 ]; then
  # Sort the lexicon with C-encoding (Is this still needed?)
  sort data/local/dict/_lexiconp.txt data/local/dict/oov_lexiconp.txt > data/local/dict/lexiconp.txt

  # deleting lexicon.txt text from a previous run, utils/prepare_lang.sh will regenerate it
  rm data/local/dict/lexicon.txt

  unixtime=$(date +%s)
  # Move old lang dir if it exists
  mkdir -p data/lang/old_$unixtime/
  mv data/lang/* data/lang/old_$unixtime/

  echo "Preparing the data/lang directory...."

  # Prepare phoneme data for Kaldi
  utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

  echo "Done!"
fi

if [ $stage -le 6 ]; then
  # Now make MFCC features.
  for x in train dev test; do
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x
  done
fi

# Todo: download source sentence archive for LM building

if [ $stage -le 7 ]; then
  mkdir -p data/local/lm/

  if [ ! -f data/local/lm/cleaned.gz ]
  then
      wget --directory-prefix=data/local/lm/ http://speech.tools/kaldi_tuda_de/German_sentences_8mil_filtered_maryfied.txt.gz
      mv data/local/lm/German_sentences_8mil_filtered_maryfied.txt.gz data/local/lm/cleaned.gz
  fi

  # Prepare ARPA LM

  # If you wont to build your own:
  local/build_lm.sh

  # Otherwise you can also use the supplied LM:
  # wget speechdata-LM.arpa

  # Transform LM into Kaldi LM format 
  local/format_data.sh

fi

# Here we start the AM
# This is adapted from https://github.com/kaldi-asr/kaldi/blob/master/egs/swbd/s5c/run.sh

if [ $stage -le 8 ]; then
  # Use the first 4k sentences as dev set.  Note: when we trained the LM, we used
  # the 1st 10k sentences as dev set, so the 1st 4k won't have been used in the
  # LM training data.   However, they will be in the lexicon, plus speakers
  # may overlap, so it's still not quite equivalent to a test set.
  utils/subset_data_dir.sh --first data/train 4000 data/train_dev # 5hr 6min
  
  # currently we do not have a  segments file as in swbd:
  if [ -f data/train/segments ]; then
    n=$[`cat data/train/segments | wc -l` - 4000]
  else
    n=$[`cat data/train/wav.scp | wc -l` - 4000]
  fi
  
  utils/subset_data_dir.sh --last data/train $n data/train_nodev

  # 55526 utterances in kaldi tuda de
  # (1/5 of swbd - 260k utterances)
  # we adapted the swbd numbers by dividing them by 5

  # original swbd comment:
  # Now-- there are 260k utterances (313hr 23min), and we want to start the
  # monophone training on relatively short utterances (easier to align), but not
  # only the shortest ones (mostly uh-huh).  So take the 100k shortest ones, and
  # then take 30k random utterances from those (about 12hr)

  utils/subset_data_dir.sh --shortest data/train_nodev 20000 data/train_100kshort #(swbd default: 100k)
  utils/subset_data_dir.sh data/train_100kshort 10000 data/train_30kshort #(swbd default: 30k)

  # Take the first 100k utterances (just under half the data); we'll use
  # this for later stages of training.
  utils/subset_data_dir.sh --first data/train_nodev 20000 data/train_100k

  # since there are more repetitions in kaldi-tuda-de compared to swbd, we upped the max repetitions a bit 200 -> 1000
  utils/data/remove_dup_utts.sh 1000 data/train_100k data/train_100k_nodup  # 110hr

  # Finally, the full training set:
  # since there are more repetitions in kaldi-tuda-de compared to swbd, we upped the max repetitions a bit 300 -> 1000
  utils/data/remove_dup_utts.sh 1000 data/train_nodev data/train_nodup  # 286hr

  #if [ ! -d data/lang_nosp ]; then 
  #  echo "Copying data/lang to data/lang_nosp..."
  #  cp -R data/lang data/lang_nosp
  #fi
fi

if [ $stage -le 9 ]; then
  ## Starting basic training on MFCC features
  steps/train_mono.sh --nj $nJobs --cmd "$train_cmd" \
                      data/train_30kshort data/lang_nosp exp/mono
fi

if [ $stage -le 10 ]; then
    steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
                    data/train_100k_nodup data/lang_nosp exp/mono exp/mono_ali

    steps/train_deltas.sh --cmd "$train_cmd" \
                        3200 30000 data/train_100k_nodup data/lang_nosp exp/mono_ali exp/tri1

    graph_dir=exp/tri1/graph_nosp
    $train_cmd $graph_dir/mkgraph.log \
               utils/mkgraph.sh data/lang_test exp/tri1 $graph_dir
    
    for dset in dev test; do
        steps/decode_si.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
                       $graph_dir data/${dset} exp/tri1/decode_${dset}_nosp
    done
    
fi

if [ $stage -le 11 ]; then
  steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
                    data/train_100k_nodup data/lang_nosp exp/tri1 exp/tri1_ali

  steps/train_deltas.sh --cmd "$train_cmd" \
                        4000 70000 data/train_100k_nodup data/lang_nosp exp/tri1_ali exp/tri2

    # The previous mkgraph might be writing to this file.  If the previous mkgraph
    # is not running, you can remove this loop and this mkgraph will create it.
#    while [ ! -s data/lang_nosp_sw1_tg/tmp/CLG_3_1.fst ]; do sleep 60; done
#    sleep 20; # in case still writing.
    graph_dir=exp/tri2/graph_nosp
    $train_cmd $graph_dir/mkgraph.log \
               utils/mkgraph.sh data/lang_test exp/tri2 $graph_dir

    for dset in dev test; do
        steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
                    $graph_dir data/${dset} exp/tri2/decode_${dset}_nosp
    done
fi

if [ $stage -le 12 ]; then
  # The 100k_nodup data is used in the nnet2 recipe.
  steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
                    data/train_100k_nodup data/lang_nosp exp/tri2 exp/tri2_ali_100k_nodup

  # From now, we start using all of the data (except some duplicates of common
  # utterances, which don't really contribute much).
  steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
                    data/train_nodup data/lang_nosp exp/tri2 exp/tri2_ali_nodup

  # Do another iteration of LDA+MLLT training, on all the data.
  steps/train_lda_mllt.sh --cmd "$train_cmd" \
                          6000 140000 data/train_nodup data/lang_nosp exp/tri2_ali_nodup exp/tri3

  graph_dir=exp/tri3/graph_nosp
  $train_cmd $graph_dir/mkgraph.log \
             utils/mkgraph.sh data/lang_test exp/tri3 $graph_dir

  for dset in dev test; do
      steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
                  $graph_dir data/${dset} exp/tri3/decode_${dset}_nosp
  done
fi

exit

if [ $stage -le 13 ]; then
  # Now we compute the pronunciation and silence probabilities from training data,
  # and re-create the lang directory.
  steps/get_prons.sh --cmd "$train_cmd" data/train_nodup data/lang_nosp exp/tri3
  utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  data/local/dict_nosp exp/tri3/pron_counts_nowb.txt exp/tri3/sil_counts_nowb.txt \
                                  exp/tri3/pron_bigram_counts_nowb.txt data/local/dict

  utils/prepare_lang.sh data/local/dict "<unk>" data/local/lang data/lang
 
  local/format_data.sh

#  LM=data/local/lm/sw1.o3g.kn.gz
#  srilm_opts="-subset -prune-lowprobs -unk -tolower -order 3"
#  utils/format_lm_sri.sh --srilm-opts "$srilm_opts" \
#                         data/lang $LM data/local/dict/lexicon.txt data/lang_sw1_tg

#  LM=data/local/lm/sw1_fsh.o4g.kn.gz
#  if $has_fisher; then
#    utils/build_const_arpa_lm.sh $LM data/lang data/lang_sw1_fsh_fg
#  fi

  graph_dir=exp/tri3/graph_sw1_tg
  $train_cmd $graph_dir/mkgraph.log \
             utils/mkgraph.sh data/lang_test exp/tri3 $graph_dir
  
  for dset in dev test; do
      steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
                  $graph_dir data/${dset} exp/tri3/decode_${dset}_sw1_tg
  done
fi

if [ $stage -le 14 ]; then
  # Train tri4, which is LDA+MLLT+SAT, on all the (nodup) data.
  steps/align_fmllr.sh --nj $nJobs --cmd "$train_cmd" \
                       data/train_nodup data/lang exp/tri3 exp/tri3_ali_nodup


  steps/train_sat.sh  --cmd "$train_cmd" \
                      11500 200000 data/train_nodup data/lang exp/tri3_ali_nodup exp/tri4

  graph_dir=exp/tri4/graph_sw1_tg
  $train_cmd $graph_dir/mkgraph.log \
             utils/mkgraph.sh data/lang_test exp/tri4 $graph_dir

  for dset in dev test; do
      steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
                      --config conf/decode.config \
                      $graph_dir data/${dset} exp/tri4/decode_${dset}_sw1_tg
  done

  # Will be used for confidence calibration example,
  #steps/decode_fmllr.sh --nj $nJobs --cmd "$decode_cmd" \
  #                      $graph_dir data/train_dev exp/tri4/decode_dev_sw1_tg
  #if $has_fisher; then
  #  steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
    #    data/lang_sw1_{tg,fsh_fg} data/eval2000 \
    #    exp/tri4/decode_eval2000_sw1_{tg,fsh_fg}
    #fi
 # ) &
fi

# Let's create a subset with 10k segments to make quick flat-start training:
# utils/subset_data_dir.sh data/train 10000 data/train.10K || exit 1;

#local/run_am.sh
#local/run_dnn.sh

