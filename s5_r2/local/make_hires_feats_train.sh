. path.sh
. cmd.sh

mfccdir=mfcc
stage=0
nJobs=8

if [ $stage -le 6 ]; then
  # Now make MFCC features.
  
  #x=tuda_train

for x in dev_e test_e; do  
#  for x in dev_a dev_b dev_c dev_d test_a test_b test_c test_d; do

    utils/copy_data_dir.sh data/$x data/${x}_hires
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs --mfcc-config conf/mfcc_hires.conf data/${x}_hires exp/make_mfcc/${x}_hires $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/compute_cmvn_stats.sh data/${x}_hires exp/make_mfcc/${x}_hires $mfccdir
    utils/fix_data_dir.sh data/${x}_hires

    steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj $nJobs data/${x}_hires/ exp/nnet3_cleaned/extractor/ exp/nnet3_cleaned/ivectors_${x}_hires

  done
fi
