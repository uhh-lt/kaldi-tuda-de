#!/bin/bash

model_name=de_350k_nnet3chain_tdnn1f_1024_sp_bi
model_path=exp/chain_cleaned/tdnn1f_1024_sp_bi
graph_dir=$model_path/graph_300k3
ivector_extractor=exp/nnet3_cleaned/extractor
ivector_extractor_conf=exp/nnet3_cleaned/ivectors_train_cleaned_sp_hires_comb/conf

rm -rf $model_name

mkdir $model_name

echo "building tar.bz2 for $model_path"
echo "using graph dir $graph_dir"
echo "and ivector extractor $ivector_extractor"

echo "copying model and fst to $model_name"

cp $model_path/final.mdl $model_name/
cp -r $graph_dir/* $model_name/
cp -r conf $model_name/

rm -rf $model_name/conf/old

echo "copying ivector extractor"

mkdir $model_name/ivector_extractor/

cp $ivector_extractor_conf/ivector_extractor.conf $model_name/ivector_extractor/
cp $ivector_extractor_conf/splice.conf $model_name/ivector_extractor/
cp $ivector_extractor/final.mat $model_name/ivector_extractor/
cp $ivector_extractor/final.dubm $model_name/ivector_extractor/
cp $ivector_extractor/online_cmvn.conf $model_name/ivector_extractor/
cp $ivector_extractor/final.ie $model_name/ivector_extractor/
cp $ivector_extractor/final.ie.id $model_name/ivector_extractor/
cp $ivector_extractor/global_cmvn.stats $model_name/ivector_extractor/
cp $ivector_extractor/splice_opts $model_name/ivector_extractor/

echo "finished copying. Now creating ${model_name}.tar.bz2..."

tar cfvj ${model_name}.tar.bz2 $model_name

echo "done"
