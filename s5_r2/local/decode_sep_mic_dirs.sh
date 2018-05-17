#!/bin/bash

. path.sh
. cmd.sh

graph_dir=exp/tri4/graph_pron
for dset in dev_a dev_b dev_c dev_d dev_e test_a test_b test_c test_d test_e; do
    echo "Now decoding $dset with GMM-HMM model" 
    steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
                 $graph_dir data/${dset} exp/tri4/decode_${dset}_pron
done

nnet3_affix=_cleaned
dir=exp/chain_cleaned/tdnn1f_sp_bi/

for dset in dev_a dev_b dev_c dev_d dev_e; do
    echo "Now decoding $dset with TDNN-HMM model"
    steps/nnet3/decode.sh --num-threads 4 --nj $nDecodeJobs --cmd "$decode_cmd" \
        --acwt 1.0 --post-decode-acwt 10.0 \
        --online-ivector-dir exp/nnet3${nnet3_affix}/ivectors_dev_hires \
        --scoring-opts "--min-lmwt 5 " \
       $dir/graph data/${dset}_hires $dir/decode_${dset} || exit 1;
    #  steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" data/lang data/lang_rescore \
    #    data/${dset}_hires ${dir}/decode_${dset} ${dir}/decode_${dset}_rescore || exit 1
done


for dset in test_a test_b test_c test_d test_e; do
    echo "Now decoding $dset with TDNN-HMM model"
    steps/nnet3/decode.sh --num-threads 4 --nj $nDecodeJobs --cmd "$decode_cmd" \
        --acwt 1.0 --post-decode-acwt 10.0 \
        --online-ivector-dir exp/nnet3${nnet3_affix}/ivectors_test_hires \
        --scoring-opts "--min-lmwt 5 " \
         $dir/graph data/${dset}_hires $dir/decode_${dset} || exit 1;
    #  steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" data/lang data/lang_rescore \
    #    data/${dset}_hires ${dir}/decode_${dset} ${dir}/decode_${dset}_rescore || exit 1
done

