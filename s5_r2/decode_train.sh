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

. path.sh
. cmd.sh

stage=0
nnet3_affix=_cleaned
dir=exp/chain_cleaned/tdnn1f_1024_sp_bi/

gmm_decode_stage=0
tdnn_decode_stage=0

# uncomment these if you would like to rescore only
# gmm_decode_stage=6
# tdnn_decode_stage=3

. utils/parse_options.sh

if [ $stage -le 1 ]; then

  graph_dir=exp/tri4/graph_pron
  
  dset=tuda_train

  #for dset in dev test; do
      echo "Now decoding $dset with GMM-HMM model" 
      steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config --stage $gmm_decode_stage \
                   $graph_dir data/${dset} exp/tri4/decode_${dset}_pron
  #done
fi

if [ $stage -le 2 ]; then
  dset=tuda_train
  #for dset in dev test; do
      echo "Now decoding $dset with TDNN-HMM model"
      steps/nnet3/decode.sh --num-threads 4 --nj $nDecodeJobs --cmd "$decode_cmd" --stage $tdnn_decode_stage \
          --acwt 1.0 --post-decode-acwt 10.0 \
          --online-ivector-dir exp/nnet3${nnet3_affix}/ivectors_${dset}_hires \
          --scoring-opts "--min-lmwt 5 " \
         $dir/graph data/${dset}_hires $dir/decode_${dset} || exit 1;
      #  steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" data/lang data/lang_rescore \
      #    data/${dset}_hires ${dir}/decode_${dset} ${dir}/decode_${dset}_rescore || exit 1
  #done
fi
