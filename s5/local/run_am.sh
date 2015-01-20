# Copyright 2015 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
# Copyright 2014 QCRI (author: Ahmed Ali)
#
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

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

echo "training jobs: $nJobs"
echo "decode jobs: $nDecodeJobs"

# Here we start the AM

# Train monophone models (right now makes no sense to do it only on a subset)
# Note: the --boost-silence option should probably be omitted by default
steps/train_mono.sh --nj $nJobs --cmd "$train_cmd" \
  data/train data/lang exp/mono || exit 1;

# Get alignments from monophone system.
steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
  data/train data/lang exp/mono exp/mono_ali || exit 1;

# train tri1 [first triphone pass]
steps/train_deltas.sh --cmd "$train_cmd" \
  2500 30000 data/train data/lang exp/mono_ali exp/tri1 || exit 1;

# First triphone decoding
time utils/mkgraph.sh data/lang_test exp/tri1 exp/tri1/graph || exit 1;
time steps/decode.sh  --nj $nDecodeJobs --cmd "$decode_cmd" \
  exp/tri1/graph data/test exp/tri1/decode

steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
  data/train data/lang exp/tri1 exp/tri1_ali || exit 1;

# Train tri2a, which is deltas+delta+deltas
steps/train_deltas.sh --cmd "$train_cmd" \
  3000 40000 data/train data/lang exp/tri1_ali exp/tri2a || exit 1;

# tri2a decoding
time utils/mkgraph.sh data/lang_test exp/tri2a exp/tri2a/graph || exit 1;
time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
  exp/tri2a/graph data/test exp/tri2a/decode

# train and decode tri2b [LDA+MLLT]
steps/train_lda_mllt.sh --cmd "$train_cmd" 4000 50000 \
  data/train data/lang exp/tri1_ali exp/tri2b || exit 1;
time utils/mkgraph.sh data/lang_test exp/tri2b exp/tri2b/graph || exit 1;
time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" exp/tri2b/graph data/test exp/tri2b/decode

# Align all data with LDA+MLLT system (tri2b)
steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
  --use-graphs true data/train data/lang exp/tri2b exp/tri2b_ali  || exit 1;

#  Do MMI on top of LDA+MLLT.
steps/make_denlats.sh --nj $nJobs --cmd "$train_cmd" \
 data/train data/lang exp/tri2b exp/tri2b_denlats || exit 1;
steps/train_mmi.sh --cmd "$train_cmd" data/train data/lang exp/tri2b_ali \
 exp/tri2b_denlats exp/tri2b_mmi || exit 1;

steps/decode.sh  --iter 4 --nj $nJobs --cmd "$decode_cmd"  exp/tri2b/graph \
 data/test exp/tri2b_mmi/decode_it4
steps/decode.sh  --iter 3 --nj $nJobs --cmd "$decode_cmd" exp/tri2b/graph \
 data/test exp/tri2b_mmi/decode_it3 # Do the same with boosting.

steps/train_mmi.sh --cmd "$train_cmd" --boost 0.05 data/train data/lang exp/tri2b_ali \
exp/tri2b_denlats exp/tri2b_mmi_b0.05 || exit 1;

steps/decode.sh  --iter 4 --nj $nJobs --cmd "$decode_cmd" exp/tri2b/graph \
 data/test exp/tri2b_mmi_b0.05/decode_it4 || exit 1;
steps/decode.sh  --iter 3 --nj $nJobs --cmd "$decode_cmd" exp/tri2b/graph \
 data/test exp/tri2b_mmi_b0.05/decode_it3 || exit 1;

# Do MPE.
steps/train_mpe.sh --cmd "$train_cmd" data/train data/lang exp/tri2b_ali exp/tri2b_denlats exp/tri2b_mpe || exit 1;

steps/decode.sh  --iter 4 --nj $nDecodeJobs --cmd "$decode_cmd" exp/tri2b/graph \
 data/test exp/tri2b_mpe/decode_it4 || exit 1;

steps/decode.sh  --iter 3 --nj $nDecodeJobs --cmd "$decode_cmd" exp/tri2b/graph \
 data/test exp/tri2b_mpe/decode_it3 || exit 1;


# From 2b system, train 3b which is LDA + MLLT + SAT.
steps/train_sat.sh --cmd "$train_cmd" \
  5000 100000 data/train data/lang exp/tri2b_ali exp/tri3b || exit 1;
utils/mkgraph.sh data/lang_test exp/tri3b exp/tri3b/graph|| exit 1;
steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
  exp/tri3b/graph data/test exp/tri3b/decode || exit 1;

# From 3b system, align all data.
steps/align_fmllr.sh --nj $nJobs --cmd "$train_cmd" \
  data/train data/lang exp/tri3b exp/tri3b_ali || exit 1;


## SGMM (subspace gaussian mixture model), excluding the "speaker-dependent weights"
steps/train_ubm.sh --cmd "$train_cmd" 700 \
 data/train data/lang exp/tri3b_ali exp/ubm5a || exit 1;

steps/train_sgmm2.sh --cmd "$train_cmd" 5000 20000 data/train data/lang exp/tri3b_ali \
  exp/ubm5a/final.ubm exp/sgmm_5a || exit 1;

utils/mkgraph.sh data/lang_test exp/sgmm_5a exp/sgmm_5a/graph || exit 1;

steps/decode_sgmm2.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
  --transform-dir exp/tri3b/decode exp/sgmm_5a/graph data/test exp/sgmm_5a/decode

steps/align_sgmm2.sh --nj $nJobs --cmd "$train_cmd" --transform-dir exp/tri3b_ali \
  --use-graphs true --use-gselect true data/train data/lang exp/sgmm_5a exp/sgmm_5a_ali || exit 1;

## boosted MMI on SGMM
steps/make_denlats_sgmm2.sh --nj $nJobs --sub-split 30 --beam 9.0 --lattice-beam 6 \
  --cmd "$decode_cmd" --transform-dir \
  exp/tri3b_ali data/train data/lang exp/sgmm_5a_ali exp/sgmm_5a_denlats || exit 1;

steps/train_mmi_sgmm2.sh --cmd "$train_cmd" --num-iters 8 --transform-dir exp/tri3b_ali --boost 0.1 \
  data/train data/lang exp/sgmm_5a exp/sgmm_5a_denlats exp/sgmm_5a_mmi_b0.1

#decode GMM MMI
utils/mkgraph.sh data/lang_test exp/sgmm_5a_mmi_b0.1 exp/sgmm_5a_mmi_b0.1/graph || exit 1;

steps/decode_sgmm2.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
  --transform-dir exp/tri3b/decode exp/sgmm_5a_mmi_b0.1/graph data/test exp/sgmm_5a_mmi_b0.1/decode

for n in 1 2 3 4; do
  steps/decode_sgmm2_rescore.sh --cmd "$decode_cmd" --iter $n --transform-dir exp/tri3b/decode data/lang_test \
    data/test exp/sgmm_5a_mmi_b0.1/decode exp/sgmm_5a_mmi_b0.1/decode$n

  steps/decode_sgmm_rescore.sh --cmd "$decode_cmd" --iter $n --transform-dir exp/tri3b/decode data/lang_test \
    data/test exp/sgmm_5a/decode exp/sgmm_5a_mmi_onlyRescoreb0.1/decode$n
done

#todo
#local/run_dnn.sh

time=$(date +"%Y-%m-%d-%H-%M-%S")
#get WER
for x in exp/*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; \
done | sort -n -r -k2 > RESULTS.$USER.$time # to make sure you keep the results timed and owned

echo training succedded
exit 0
