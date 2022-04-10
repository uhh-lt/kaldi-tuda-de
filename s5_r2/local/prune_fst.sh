#!/bin/bash

dict_suffix=_std_big_v6
prune_factor=100.0

. ./path.sh || exit 1; # for KALDI_ROOT                                                                                                                                                           

export PATH=$KALDI_ROOT/tools/kaldi_lm:$PATH

prune_lm.sh --arpa $prune_factor data/local/lm_${dict_suffix}/4gram-mincount/
./local/format_data.sh --arpa_lm data/local/lm_${dict_suffix}/4gram-mincount/lm_pr${prune_factor}.gz --lang_in_dir data/lang_${dict_suffix} --lang_out_dir data/lang_${dict_suffix}_pr${prune_factor}_test
./local/run_tdnn_1f_B.sh --stage 19 --lang-dir data/lang_${dict_suffix}_pr${prune_factor} --decode-affix _pr${prune_factor}
