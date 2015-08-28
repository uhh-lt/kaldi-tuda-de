#!/bin/bash
# Copyright 2015 TU-Darmstadt (Author: Benjamin Milde)
# Apache 2.0

mkdir exp/nnet2_dist
mkdir exp/nnet2_dist/conf
cp exp/nnet2_online/nnet_ms_a/final.mdl exp/nnet2_dist
cp exp/tri3b/graph/HCLG.fst exp/nnet2_dist
cp exp/tri3b/graph/words.txt exp/nnet2_dist
cp exp/nnet2_online/ivectors_train_hires/conf/ivector_extractor.conf exp/nnet2_dist/conf/
cp conf/mfcc_hires.conf exp/nnet2_dist/conf/mfcc.conf
cp exp/nnet2_online/ivectors_train_hires/conf/online_cmvn.conf exp/nnet2_dist/conf/
cp exp/nnet2_online/ivectors_train_hires/conf/splice.conf exp/nnet2_dist/conf/
cp -R exp/nnet2_online/extractor/ exp/nnet2_dist/
