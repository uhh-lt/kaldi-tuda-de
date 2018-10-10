. path.sh
. cmd.sh

mfccdir=mfcc
stage=0

if [ $stage -le 6 ]; then
  # Now make MFCC features.
for x in dev_e test_e; do
#  for x in dev_a dev_b dev_c dev_d test_a test_b test_c test_d; do
#  for x in train dev test; do
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x
  done
fi
