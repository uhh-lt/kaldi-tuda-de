. cmd.sh
. path.sh

# This creates features for serparates microphone dirs, useful if you want to separate WERs for the different microphones in tuda dev / test

for x in dev_a dev_b dev_c dev_d dev_e test_a test_b test_c test_d test_e; do
  echo "Creating features for: $x"
  utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
  steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
  utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
  steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
  utils/fix_data_dir.sh data/$x
done

for datadir in dev_a dev_b dev_c dev_d dev_e test_a test_b test_c test_d test_e; do
  echo "Creating features for: ${datadir}_hires"
  utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
  steps/make_mfcc.sh --nj $nJobs --mfcc-config conf/mfcc_hires.conf --cmd "$train_cmd" data/${datadir}_hires
  steps/compute_cmvn_stats.sh data/${datadir}_hires
  utils/fix_data_dir.sh data/${datadir}_hires
done
