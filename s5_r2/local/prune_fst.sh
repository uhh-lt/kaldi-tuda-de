#!/bin/bash

. ./path.sh || exit 1; # for KALDI_ROOT                                                                                                                                                           

export PATH=$KALDI_ROOT/tools/kaldi_lm:$PATH

prune_lm.sh --arpa 200.0 data/local/lm_std_big_v5/4gram-mincount/
./local/format_data.sh --arpa_lm data/local/lm_std_big_v5/4gram-mincount/lm_pr200.0.gz --lang_in_dir data/lang_std_big_v5 --lang_out_dir data/lang_std_big_v5_pr200_test
./local/run_tdnn_1f_B.sh --stage 19 --lang-dir data/lang_std_big_v5_pr200 --decode-affix _pr200
