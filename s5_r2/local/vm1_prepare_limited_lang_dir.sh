. cmd.sh
. path.sh

  # Sort the lexicon with C-encoding (Is this still needed?)
  cp data/local/dict/lexicon.txt data/local/dict/_lexicon.txt
  sort -u data/local/dict/_lexicon.txt  > data/local/dict/lexicon.txt

#  unixtime=$(date +%s)
#  # Move old lang dir if it exists
#  mkdir -p data/lang/old_$unixtime/
#  mv data/lang/* data/lang/old_$unixtime/

  echo "Preparing the data/lang directory...."

  # Prepare phoneme data for Kaldi
  utils/prepare_lang.sh data/local/vm1_dict "<UNK>" data/local/vm1_lang data/vm1_lang


#  srcdir=data/local/lang
#  dir=data/local/lm

  mkdir data/local/vm1_lm

  cut -f 2- -d" " data/vm1_train/text > data/local/vm1_lm/cleaned
  gzip data/local/vm1_lm/cleaned

  local/build_lm.sh --srcdir data/local/vm1_lang --dir data/local/vm1_lm

#  arpa_lm=data/local/lm/3gram-mincount/lm_pr16.0.gz
#  lang_out_dir=data/lang_test

  local/format_data.sh --arpa-lm data/local/vm1_lm/3gram-mincount/lm_unpruned.gz --lang-out-dir data/lang_vm1_test --lang_in_dir data/vm1_lang


  echo "Done!"

