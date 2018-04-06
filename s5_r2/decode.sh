#!/bin/bash
#
# This script shows how to use the SGMM-HMM model for decoding new data in batch mode.
# For slightly better performance, the DNN acoustic models can also be used. However,
# the SGMM model used here is faster and easier to train (no GPU needed)
#
# It assumes that you already trained all models with run.sh and that data/$decodedir
# is a new directory containing at least the files "wav.scp", "text" and "utt2spk":
#
# I.e. in data/$decodedir:
#
# wav.scp
# unique1 <filename1.wav, can be relative to the s5 directory>
# unique2 <filename2.wav>
# ...
#
# text
# unique1 None
# unique2 None
# ...
#
# utt2spk
# unique1 speaker1
# unique2 speaker2
# unique3 speaker2
# ...
#
# "wav.scp" is used to map unique identifiers to audio files (wav)
# The file "text" would usually contain manual transcriptions, which is only useful 
# if you want to evaluate the model with word error rate (WER). Here we use "None",
# since we want to use the model for an automatic transcription.
#
# Finally, the file "utt2spk" maps utterance ids to speakers
#
# See also http://kaldi.sourceforge.net/data_prep.html
# 
# You also have to set mfccJobs and mfccJobs down below to a number equal or 
# smaller than the total number of wav files in your job, otherwise you wont be
# able to decode anything!
# 

decodedir=frei_test
mfccdir=mfcc

# Check that steps and utils are probably linked:
[ ! -L "steps" ] && ln -s ../../wsj/s5/steps
[ ! -L "utils" ] && ln -s ../../wsj/s5/utils

# Now start preprocessing with KALDI scripts

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

# Path also sets LC_ALL=C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs.
if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;

fi

# This has to be set to a number equal or smaller than the total number of wav files in $decodedir ! 
mfccJobs=6
nDecodeJobs=2

echo "Runtime configuration is: nJobs $nJobs, nDecodeJobs $nDecodeJobs, mfccJobs $mfccJobs. If this is not what you want, edit decode.sh!"
echo "Warning, it has to be set to a number equal or smaller than the total number of wav files in data/$decodedir! If this is not what you want, edit decode.sh!"

# Now make MFCC features.
    
utils/fix_data_dir.sh data/$decodedir # some files fail to get mfcc for many reasons
steps/make_mfcc.sh --cmd "$train_cmd" --nj $mfccJobs data/$decodedir exp/make_mfcc/$decodedir $mfccdir
utils/fix_data_dir.sh data/$decodedir # some files fail to get mfcc for many reasons
steps/compute_cmvn_stats.sh data/$decodedir exp/make_mfcc/$decodedir $mfccdir
utils/fix_data_dir.sh data/$decodedir

# Decode with tri3b model
steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
      exp/tri3b/graph data/$decodedir exp/tri3b/decode_$decodedir || exit 1;

# Now decode with SGMM decoder
steps/decode_sgmm2.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
  --transform-dir exp/tri3b/decode_$decodedir exp/sgmm_5a/graph data/$decodedir exp/sgmm_5a/decode_$decodedir

# (Optional) rescore with large LM
steps/lmrescore_const_arpa.sh data/lang_test data/lang_const_arpa data/$decodedir exp/sgmm_5a/decode_$decodedir exp/sgmm_5a/decode_${decodedir}_rescored

# Output human readable version of the best path ( = best automatic transcript)
cat exp/sgmm_5a/decode_${decodedir}_rescored/scoring/log/best_path.13.log
