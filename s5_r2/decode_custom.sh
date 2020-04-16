#!/bin/bash

# Copyright 2018 Language Technology, Universitaet Hamburg (author: Benjamin Milde)

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

#
# This is an example script that shows how a custom test set can be decoded
#

. path.sh
. cmd.sh

stage=1
nnet3_affix=_cleaned

gmmdir=exp/tri4_cleaned
dir=exp/chain_cleaned/tdnn1f_1024_sp_bi/
#dir=exp/chain_cleaned/tdnn7o_std_sp_bi/

dir=exp/chain_cleaned/tdnn1f_2048_sp_bi/

gmm_decode_stage=0
tdnn_decode_stage=0

decode_affix=_std_big
#langdir=data/lang_test_pron
lang_dir=data/lang_std_big_test/

graph_dir=$gmmdir/graph_pron${decode_affix}

decodedir=l2go_test

mfccJobs=16

# uncomment these if you would like to rescore only
# gmm_decode_stage=6
# tdnn_decode_stage=3

. utils/parse_options.sh


#if [ $stage -le 1 ]; then
#  #Usage: utils/mkgraph.sh [options] <lang-dir> <model-dir> <graphdir>
#
#  #$train_cmd $graph_dir/mkgraph.log \
#  utils/mkgraph.sh $lang_dir $gmmdir $graph_dir
#fi
#
#if [ $stage -le 2 ]; then
#for dset in dev test dev_a dev_b dev_c dev_d test_a test_b test_c test_d; do
##  for dset in dev test; do
#      echo "Now decoding $dset with GMM-HMM model" 
#      steps/decode_fmllr.sh --nj $nDecodeJobs --num-threads 2 --cmd "$decode_cmd" --config conf/decode.config --stage $gmm_decode_stage \
#                   $graph_dir data/${dset} $gmmdir/decode${decode_affix}_${dset}_pron
#  done
#fi

if [ $stage -le 0 ]; then
#	cp -vR data/$decodedir data/${decodedir}_hires

	echo "Computing mfcc feats..."

	utils/fix_data_dir.sh data/$decodedir # some files fail to get mfcc for many reasons
	steps/make_mfcc.sh --mfcc-config conf/mfcc.conf --cmd "$train_cmd" --nj $mfccJobs data/$decodedir #exp/make_mfcc/$decodedir $mfccdir
	utils/fix_data_dir.sh data/$decodedir # some files fail to get mfcc for many reasons
	steps/compute_cmvn_stats.sh data/$decodedir exp/make_mfcc/$decodedir $mfccdir
	utils/fix_data_dir.sh data/$decodedir
fi

if [ $stage -le 1 ]; then
	
	echo "Computing hires mfcc feats..."

        utils/fix_data_dir.sh data/${decodedir}_hires # some files fail to get mfcc for many reasons
        steps/make_mfcc.sh --mfcc-config conf/mfcc_hires.conf --cmd "$train_cmd" --nj $mfccJobs data/${decodedir}_hires #exp/make_mfcc/${decodedir}_hires $mfccdir
        utils/fix_data_dir.sh data/${decodedir}_hires # some files fail to get mfcc for many reasons
        steps/compute_cmvn_stats.sh data/${decodedir}_hires exp/make_mfcc/${decodedir}_hires $mfccdir
        utils/fix_data_dir.sh data/${decodedir}_hires
fi

if [ $stage -le 2 ]; then

    echo "Extract ivectors..."
    steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj $mfccJobs data/${decodedir}_hires/ exp/nnet3_cleaned/extractor/ exp/nnet3_cleaned/ivectors_${decodedir}_hires
	# generate ivector
fi

if [ $stage -le 3 ]; then
  utils/mkgraph.sh --self-loop-scale 1.0 $lang_dir $dir $dir/graph${decode_affix}
fi

if [ $stage -le 4 ]; then
#   for dset in dev_e test_e; do
      dset=$decodedir 
# for dset in dev_a dev_b dev_c dev_d test_a test_b test_c test_d; do
#  for dset in dev test; do
      echo "Now decoding $dset with TDNN-HMM model"
      steps/nnet3/decode.sh --num-threads 4 --nj $nDecodeJobs --cmd "$decode_cmd" --stage $tdnn_decode_stage \
          --acwt 1.0 --post-decode-acwt 10.0 \
          --online-ivector-dir exp/nnet3${nnet3_affix}/ivectors_${dset}_hires \
          --scoring-opts "--min-lmwt 5 " \
         $dir/graph${decode_affix} data/${dset}_hires $dir/decode${decode_affix}_${dset} || exit 1;
      #  steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" data/lang data/lang_rescore \
      #    data/${dset}_hires ${dir}/decode_${dset} ${dir}/decode_${dset}_rescore || exit 1
 # done
fi
