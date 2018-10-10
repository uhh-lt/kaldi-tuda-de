. path.sh
. cmd.sh

mfccdir=mfcc
stage=0

if [ $stage -le 6 ]; then
  # Now make MFCC features.
  for x in vm1_dev vm1_test; do
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      utils/copy_data_dir.sh data/$x data/${x}_hires
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x
  done

  for x in vm1_dev_hires vm1_test_hires; do
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs --mfcc-config conf/mfcc_hires.conf data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
      steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
      utils/fix_data_dir.sh data/$x
  done
fi
