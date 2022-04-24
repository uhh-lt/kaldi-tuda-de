#!/bin/bash

dict_suffix=_std_big_v6
prune_factor=150.0

. ./path.sh || exit 1; # for KALDI_ROOT                                                                                                                                                           

export PATH=$KALDI_ROOT/tools/kaldi_lm:$PATH

prune_lm.sh --arpa $prune_factor data/local/lm${dict_suffix}/4gram-mincount/
./local/format_data.sh --arpa_lm data/local/lm${dict_suffix}/4gram-mincount/lm_pr${prune_factor}.gz --lang_in_dir data/lang${dict_suffix} --lang_out_dir data/lang${dict_suffix}_pr${prune_factor}_test
cp data/lang${dict_suffix}/words.txt data/lang${dict_suffix}_pr${prune_factor}_test/words.txt
./local/run_tdnn_1f.sh --stage 19 --lang-dir data/lang${dict_suffix}_pr${prune_factor} --decode-affix _pr${prune_factor}
