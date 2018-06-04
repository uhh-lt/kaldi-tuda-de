#!/bin/bash
exp_dir=exp/
for x in ${exp_dir}/{mono,tri,sgmm,nnet,dnn,lstm}*/decode*; do [ -d $x ] && [[ $x =~ "$1" ]] && grep WER $x/wer* | utils/best_wer.sh; done 2>/dev/null
for x in ${exp_dir}/chain_cleaned/tdnn*/decode*; do [ -d $x ] && [[ $x =~ "$1" ]] && grep WER $x/wer* | utils/best_wer.sh; done 2>/dev/null
exit 0
