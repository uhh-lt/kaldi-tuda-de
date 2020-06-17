# unique str so we can rerun this script
unixtime=$(date +%s)

echo "Using unixtime $unixtime as unique number in backup dirs."

mv mfcc mfcc_old_$unixtime
mkdir mfcc/

echo "Moved mfcc dir to mfcc_old_$unixtime."

mkdir data_backup_$unixtime/

mv data/train* data_backup_$unixtime/
mv data/*train data_backup_$unixtime/
mv data/dev* data_backup_$unixtime/
mv data/test* data_backup_$unixtime/
mv data/lang* data_backup_$unixtime/

echo "Cleaned up data and moved data dirs to data_backup_$unixtime/"

#commonvoice_train  dev_a  dev_c  lang_std_big3                lang_std_big3_test  lang_std_big4_test  lexicon_ids.txt  m_ailabs_train  swc_train_v2.tar.gz  test_a  test_c  train       train_100k_nodup  train_30kshort  train_nodev  train_without_commonvoice  tuda_train  waveIDs.txt
#dev                dev_b  dev_d  lang_std_big3_nosp_std_big3  lang_std_big4       lexicon             local            swc_train       test                 test_b  test_d  train_100k  train_100kshort   train_dev       train_nodup  train_without_mailabs      wav

mv exp/ exp_$unixtime/
mkdir exp/

echo "Moved model from exp/ to exp_$unixtime/"
