# Open source speech recognition recipe and corpus for building German acoustic models with Kaldi

   * [Open source speech recognition recipe and corpus for building German acoustic models with Kaldi](#open-source-speech-recognition-recipe-and-corpus-for-building-german-acoustic-models-with-kaldi)
      * [News](#news)
      * [Pretrained models](#pretrained-models)
   * [Training your own models](#training-your-own-models)
      * [Prerequisites](#prerequisites)
      * [Get LM text data](#Get-LM-text-data)
      * [Building the acoustic models](#building-the-acoustic-models)
      * [Getting data files separately](#getting-data-files-separately)
         * [Speech corpus](#speech-corpus)
         * [German language texts](#german-language-texts)
         * [German phoneme dictionary](#german-phoneme-dictionary)
   * [References](#references)

This recipe and collection of scripts enables you to train large vocabulary German acoustic models for speaker-independent automatic speech recognition (ASR) with [Kaldi](http://kaldi.sourceforge.net/). The scripts currently use three freely available German speech corpora: The Tuda-De corpus is recorded with a Microsoft Kinect and two other microphones in parallel at Technische Universität Darmstadt and has been released under a permissive license [(CC-BY 4.0)](http://creativecommons.org/licenses/by/4.0/). This corpus compromises ~31h of training data per microphone and ~5h separated into development and test partitions. We also make use of the German subset from the [Spoken Wikipedia Corpora (SWC)](https://nats.gitlab.io/swc/), containing about 285h of additional data and the German subset of [m-ailabs read speech data corpus](http://www.m-ailabs.bayern/en/the-mailabs-speech-dataset/) [(mirror)](https://www.caito.de/2019/01/the-m-ailabs-speech-dataset/) (237h). Recently we also added the German Commonvoice corpus from Mozilla (https://commonvoice.mozilla.org/de) with 370h of data. We use the test/dev sets from Tuda-De for WER evaluations.

The newest recipe (s5\_r2) trains and tests on data from multiple microphones by default (all but Realtek - about 127h of audio in total). By editing run.sh you can also restrict it to a single microphone (e.g. only Kinect). It also trains on SWC data and M-ailabs by default, too, resulting in 630h of speech data in total after cleaning. See [our paper](https://arxiv.org/abs/1807.10311) for more information and WER results. More recent results are in the table in the [pretrained models](#Newest-pretrained-models) section.

The old s5 recipe used in [our previous paper](https://www.inf.uni-hamburg.de/en/inst/ab/lt/publications/2015-radeck-arnethetal-tsd2015-speechcorpus.pdf) is also still available and trained only on the beamformed data of the Kinect microphone, checkout the README.md in the s5 directory if you want to reproduce the results of our old paper.  

The scripts will ask you where to place larger files and can download all necessary files (speech corpus, German texts, phoneme dictionaries) to train the acoustic and language models. You can also download these resources manually, see Section "Getting data files separately" down below.

**If you use our data, models or scripts in your academic work please cite our [paper](#references)!**

## News

19 April 2022
- We updated the LM (v6) and recrawled recent text data and extended the vocabulary (now 900k). Our newest best result (with 140 million sentences) is 6.19% WER on Tuda-De Dev and 6.93% WER on Tuda-De Test. See our newest pre-trained models here: [pretrained models](#Newest-pretrained-models). If you need an overall faster model, you can also replace the default HCLG with this much smaller one: [HCLG_s](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_900k_HCLG_s.fst.bz2). 

4 April 2022
- We added the newest Common voice data (version 8), bringing the total training amount to 1700 hours! We also added a const arpa and rnn lm model for this new model. Our best result with rescoring is now a WER of 6.51 on Tuda-De dev and 7.43 on Tuda-De test!
Currently, you can find the training scripts for this new model in the CV7 branch: https://github.com/uhh-lt/kaldi-tuda-de/tree/CV7
We'll soon merge them to the master branch.

- The Tuda-De dataset also got updated to version 4, this release includes several fixed utterances. Thank you again, Sven Hartrumpf!

6 April 2021 
- We have added const arpa language models for rescoring (trained on 100 million sentences). These did reduce error rates further, our best result on tuda-de test is 11.85% WER now. A pre-trained RNN-LM will soon be available as well.

2 July 2020
- We have added two new pretrained models: tuda_swc_mailabs_cv_voc683k and tuda_swc_mailabs_cv_voc683k_smaller_fst, both trained on 1000h of speech data and with our new LM.
- The new model has a 13% lower WER on tuda-test. It also contains many more new and uptodate words and a better phoneme lexicon. See [pretrained models](#pretrained-models) for more details and download links.
- You can also check out [kaldi-model-server](https://github.com/uhh-lt/kaldi-model-server), our PyKaldi based solution to easily load our Kaldi models.

12 June 2020

- We have added the Common Voice (de) dataset, the total amount of training data is over 1000h now!
- We added a new language model (LM) trained on 100 million normalized German sentences, with recent data as well
- We now ship a pre-trained ARPA for the LM, but you can also crawl and normalize your own data with the steps detailed in https://github.com/bmilde/german-asr-lm-tools/
- Some errors in the phoneme inventory have been corrected. You will need to train the new model from scratch, as the phoneme inventories are incompatible.
- A new manual lexicon resource has been added to kaldi-tuda-de, with recent words as well. Adds 13K+ manually verified lexicon words in X-SAMPA-DE format. See https://github.com/uhh-lt/kaldi-tuda-de/blob/master/s5_r2/local/de_extra_lexicon.txt
- We created a lexicon editor to add and verify manual phoneme entries with active learning: https://github.com/uhh-lt/speech-lex-edit
- New pre-trained ASR models will follow shortly

5 March 2019

- A new pretrained model with a vocabulary of 400 thousand words is available: [download](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_400k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2)

- We added more aligned speech data (630h total now), thanks to the [m-ailabs speech data corpus](http://www.m-ailabs.bayern/en/the-mailabs-speech-dataset/) [(mirror)](https://www.caito.de/2019/01/the-m-ailabs-speech-dataset/). We also thank Pavel Denisov for sending us a Kaldi data preparation script for this new open source corpus.

21 August 2018

- A new pretrained model with a vocabulary of 350 thousand words is available: [download](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_350k_nnet3chain_tdnn1f_1024_sp_bi.tar.bz2)

- This model is also the best performing one in [our paper](https://arxiv.org/abs/1807.10311).

- This model has also been succesfully tested in the popular [Kaldi Gstreamer Server software](https://github.com/alumae/kaldi-gstreamer-server). The paths in this package are organized according to the Kaldi Gstreamer examples, a matching kaldi_tuda_de_nnet3_chain.yaml configuration file is included. A worker startup script is also included (run_tuda_de.sh), but you will probably need to change paths. See also the Kaldi + Gstreamer Server Software installation guide [here](https://raw.githubusercontent.com/bmilde/ambientsearch/master/INSTALL_KALDI).

15 August 2018

- We thank Sven Hartrumpf for fixing xml files with incorrect transcriptions in the Tuda corpus! A new release of the corpus data will soon be available.

26 July 2018

- Our paper "Open Source Automatic Speech Recognition for German" is accepted at [ITG2018](https://www.uni-oldenburg.de/itg2018/) (10.-12. October 2018, Oldenburg, Germany)! [A preprint of the paper is available here](https://arxiv.org/abs/1807.10311). 

26 June 2018

- We moved the repository from tudarmstadt-lt to [language technologies](https://www.inf.uni-hamburg.de/en/inst/ab/lt/home.html) new uhh-lt github repository.

- The ivector extractor had been missing from the acoustic model binary archive. You can download it separately from  https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/tdnn_chain_cleaned_tuda_swc_voc126k_ivector_extractor.tar.bz2 or redownload the [full archive](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/tdnn_chain_cleaned_tuda_swc_voc126k.tar.bz2).

31 May 2018

- A pre-trained TDNN-HMM chain model for German can now be downloaded from this address: https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/tdnn_chain_cleaned_tuda_swc_voc126k.tar.bz2

- Vocabulary: 126794 words, trained on tuda-de and SWC (268h combined). Contains all the content of the exp/chain_cleaned directory, also decoding lattices of tuda test/dev. See https://github.com/alumae/kaldi-gstreamer-server and https://github.com/jcsilva/docker-kaldi-gstreamer-server for a nice full-duplex server API for Kaldi models, you should be able to use our models there, too.

30 May 2018

- We have added the option to train with additional data from the SWC corpus. See https://nats.gitlab.io/swc/ for more information on this dataset. The combined amount of training data is now around 268 hours.

02 May 2018

- A recipe to train TDNN-HMM chain acoustic models is now available, similar to TED-LIUMs egs. See: https://github.com/tudarmstadt-lt/kaldi-tuda-de/blob/master/s5_r2/local/run_tdnn_1f.sh

25 April 2018

- New s5_r2 recipe adapted from swbd s5c (GMM-HMM at the moment, TDNN recipe coming soon)!
- s5_r2 local scripts are now compatible with Python3
- Training on all microphones data is now possible and also the default
- Instead of MARYs phonemizer for OOV words, sequitur G2P is now used
- Updated Kaldi install instructions

## Newest pretrained models

| Acoustic model + FST | Training data | Tuda dev WER (FST) | Tuda test WER (FST) |
| --- | --- | --- | --- |
| [tuda_swc_mailabs_cv8_voc900k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_900k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2) | 1700h (tuda+SWC+m-ailabs+cv8) | 9.30  | 10.17 |
| + [lm_v6_voc900k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_900k_const_arpa.tar.bz2) const arpa rescoring | 140 million sentences | 7.23 | 7.96  |
| + [rnn_lmv6_lstm4x_voc900k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_900k_rnnlm_lstm_4x.tar.bz2) rnnlm rescoring | 140 million sentences | **6.19** | **6.93** |

All results above are with [number reformating](https://github.com/bmilde/german-asr-lm-tools/blob/master/normalize_numbers.py), e.g. drei und sechzig -> dreiundsechzig. If you need an overall faster model, you can also replace the default HCLG with this much smaller one: [HCLG_s](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_900k_HCLG_s.fst.bz2). Together with RNNLM rescoring, the WER result will only be minimally bigger.

## Previous pretrained models

| Acoustic model + FST | Training data | Tuda dev WER (FST) | Tuda test WER (FST) |
| --- | --- | --- | --- |
| [tuda_swc_voc126k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/tdnn_chain_cleaned_tuda_swc_voc126k.tar.bz2) / [mirror](http://speech.tools/kaldi_tuda_de/tdnn_chain_cleaned_tuda_swc_voc126k.tar.bz2) | 375h (tuda+SWC) | 20.30 | 21.43 |
| [tuda_swc_voc350k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_350k_nnet3chain_tdnn1f_1024_sp_bi.tar.bz2) / [mirror](http://speech.tools/kaldi_tuda_de/de_350k_nnet3chain_tdnn1f_1024_sp_bi.tar.bz2) | 375h (tuda+SWC) | 15.32 | 16.49 |
| [tuda_swc_mailabs_voc400k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_400k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2) / [mirror](http://speech.tools/kaldi_tuda_de/de_400k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2) | 630h (tuda+SWC+m-ailabs) | 14.78 | 15.87 |
| [tuda_swc_mailabs_cv_voc683k_smaller_fst](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_683k_nnet3chain_tdnn1f_2048_sp_bi_smaller_fst.tar.bz2) | 1000h (tuda+SWC+m-ailabs+cv) | 12.69 | 14.29 |
| + [lm_v5_voc683k_smaller_fst](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/carpa_rescoring_language_model_v5_voc683k.tar.bz2) const arpa rescoring | 100 million sentences | 10.92 | 12.37 |
| + [reformat numbers](https://github.com/bmilde/german-asr-lm-tools/blob/master/normalize_numbers.py) | e.g. drei und sechzig -> dreiundsechzig |  8.94  | 10.26 |
| [tuda_swc_mailabs_cv3_voc683k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_683k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2) | 1000h (tuda+SWC+m-ailabs+cv3) | 12.26 | 13.79 |
| + [lm_v5_voc683k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/carpa_rescoring_language_model_v5_voc683k.tar.bz2) const arpa rescoring | 100 million sentences | 10.47 | 11.85 |
| + [reformat numbers](https://github.com/bmilde/german-asr-lm-tools/blob/master/normalize_numbers.py) | e.g. drei und sechzig -> dreiundsechzig | 8.61  | 9.85 |
| [tuda_swc_mailabs_cv8_voc722k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_722k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2) | 1700h (tuda+SWC+m-ailabs+cv8) | 10.94 | 12.09 |
| + [lm_v5_voc722k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_722k_const_arpa.tar.bz2) const arpa rescoring | 100 million sentences | 9.25 | 10.17 |
| + [reformat numbers](https://github.com/bmilde/german-asr-lm-tools/blob/master/normalize_numbers.py) | e.g. drei und sechzig -> dreiundsechzig | 7.51 | 8.53 |
| + [rnn_lm_lstm2x_voc722k](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_722k_rnnlm_lstm_2x.tar.bz2) rnnlm rescoring | 100 million sentences | **6.51** | **7.43** |

New: We have now added results for rescoring as well, which improves the FST decoding results further as expected. This includes both const arpa models as well as RNN LMs, see also [our paper](https://arxiv.org/abs/1807.10311). 

We have developed a PyKaldi based solution to use the models with either a local microphone or network streaming in real time: https://github.com/uhh-lt/kaldi-model-server

For batch decoding of media files, we developped [subtitle2go](https://github.com/uhh-lt/subtitle2go) to automatically generate German subtitles.

Another option to use the models is the [Kaldi gstreamer server project](https://github.com/alumae/kaldi-gstreamer-server). You can either stream audio and do online (real-time) recogniton with it or send wav files via http and get a JSON result back. See also the Kaldi + Gstreamer Server Software installation guide [here](https://raw.githubusercontent.com/bmilde/ambientsearch/master/INSTALL_KALDI). There is a run_tuda_de.sh in the package that starts Kaldi gstreamer workers for tuda_de. You will need to modify the KALDI_ROOT variable in the script so that it finds your Kaldi installation properly.

# Training your own models

If you want to adapt our models (add training data, augment training data, change vocabulary, ...), you will need to retrain our models. A workstation or server with more than 64GB memory might be needed, having access to a lot of CPU cores is recommended and a recent Nvidia GPU is needed to train neural models such as the TDNN-HMM.

## Prerequisites

Clone the repository with the submodule:
```
git clone --recurse-submodules https://github.com/uhh-lt/kaldi-tuda-de
```


The scripts are only tested under Linux (Ubuntu 16.04 - 20.04). Install at first some mandatory packages:
```
sudo apt install sox libsox-fmt-all
```

Download and install Kaldi and follow the installation instructions. You can download a recent version using git:

```
 git clone https://github.com/kaldi-asr/kaldi.git kaldi-trunk --origin golden
```

In Kaldi trunk:

1. go to tools/  and follow INSTALL instructions there.

2. Install a BLAS library. This can be Intel MKL, OpenBLAS or Atlas.

If you have an Intel CPU the easist and now recommended library is to install Intel MKL. You can install it easily on Debian/Ubuntu by running extras/install_mkl.sh. You can then skip the rest of this section and go to section 3.

Cross platform solution: Download and install OpenBLAS, build a non-multithreading (important!) library with:

```
make USE_THREAD=0 USE_LOCKING=1 FC=gfortran
```

Now follow the displayed instructions to install OpenBLAS headers and libs to a new and empty directory. 

**Warning! It is imperative to build a single threaded OpenBLAS library**, otherwise you will encounter hard to debug problems with Kaldi as Kaldis parallelization interferes with the OpenBLAS one.

3. go to src/ and follow INSTALL instructions there. Intel MKL is found automatically, if you installed with OpenBLAS point the configure script to your OpenBLAS installation (see ./configure --help).

**Our scripts are meant to be placed into its own directory in KALDIs egs/ directory.** This is also where all the other recipes reside in. If you want to build DNN models, you probably want to enable CUDA in KALDI with the configure script in src/. You should have a relatively recent Nvidia GPU, at least one with the Kepler architecture.

You also need Sequitur G2P (https://www-i6.informatik.rwth-aachen.de/web/Software/g2p.html, https://github.com/sequitur-g2p/sequitur-g2p). Download the package and run make, then edit the sequitur\_g2p variable in s5\_r2/cmd.sh to point to the g2p.py script.  

You will also need a recent version of Python 3. Package requirements are:

```
pip3 install beautifulsoup4 lxml spacy && python -m spacy download de_core_news_lg
```

Additinally, the requests package was previously used to communicate with MaryTTS to generate phonemizations, however you won't need it if you run the standard setup.

## Get LM text data

See https://github.com/bmilde/german-asr-lm-tools/ for instructions on getting recent German text data normalized. 
Place the resulting gzipped file in ${lm_dir}/cleaned_lm_text.gz, with the defaults: data/local/lm_std_big_v6/cleaned_lm_text.gz
If you forget this step, the run.sh script will complain about a missing LM text file.
Warning: The default vocabulary file local/voc_800k.txt may give suboptimal WER results, if you pair it with your own crawled data, so make sure to replace it with your own vocabulary file. 

## Building the acoustic models

After you have installed the prerequisites, edit cmd.sh in the s5\_r2/ directory of this distribution to adjust for the number of processors you have locally (change nJobs and nDecodeJobs accordingly). You could probably also uncomment the cluster configuration and run the scripts on a cluster, but this is untested and may require some tinkering to get it running.

Then, simply run ./run.sh in s5_r2/ to build the acoustic and language models. The script will ask you where to place larger files (feature vectors and KALDI models) and automatically build appropriate symlinks. [Kaldi_lm](http://www.danielpovey.com/files/kaldi/kaldi_lm.tar.gz) is automatically downloaded and compiled if it is not found on your system and standard Kneser-Ney is used for a 4-gram LM.

## Getting data files separately

You can of course also use and download our data resources separately.

### Speech corpus

The corpus can be downloaded [here](https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/german-speechdata-package-v2.tar.gz). The license is [CC-BY 4.0](http://creativecommons.org/licenses/by/4.0/).
The run.sh script expects to find the corpus data extracted in data/wav/ and will download it for you automatically, if it does not find the data.

Newer recipes also make use of [SWC data](https://nats.gitlab.io/swc/).

### German language texts

See https://github.com/bmilde/german-asr-lm-tools/ for new instructions to obtain a large amount of German LM text data.

### German phoneme dictionary

The phoneme dictionary is currently not supplied with this distribution, but the scripts to generate them are. DFKIs MARY includes a nice [LGPL German phoneme dictionary](https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt) with ~26k entries. Other sources for phoneme dictionary entries can be found at [BAS](ftp://ftp.bas.uni-muenchen.de/pub/BAS). Our parser understands the different formats of     [VM.German.Wordforms](ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/VM.German.Wordforms), [RVG1_read.lex](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_read.lex), [RVG1_trl.lex](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_trl.lex) and [LEXICON.TBL](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG-J/LEXICON.TBL).
The final dictionary covers ~44.8k unique German words with 70k entries total (pronunciation variants). Since the licensing of the BAS dictionaries is unclear, they are not included into the phoneme dictionary by default. You can however enable them by editing the header of run.sh and setting use_BAS_dictionaries to true.

build_big_lexicon.py can import many dictionaries in the [BasSAMPA](http://www.bas.uni-muenchen.de/Bas/BasSAMPA)  format and merge them into a single dictionary. Its parser understand many variants and dialects of BasSAMPA and the adhoc dictionary formats. To support new variants you'll have to edit def guessImportFunc(filename). The output is a serialised python object.

export_lexicon.py will export such a serialised python dictionary into KALDIs [lexion_p.txt](http://kaldi.sourceforge.net/data_prep.html#data_prep_lang_creating) format (this allows to model different phonetic realisations of the same word with probabilities). Stress markers in the phoneme set are grouped with their unstressed equivalents in KALDI using the extra_questions.txt file. It is also possible to generate a CMU Sphinx formated dictionary with the same data using the -spx option. The Sphinx format also allows pronunciation variants, but cannot model probabilities for these variants.

See also:
```
python3 s5_r2/local/build_big_lexicon.py --help
python3 s5_r2/local/export_lexicon.py --help
```

# References

If you use our scripts and/or data in your academic work please cite:

```
@InProceedings{milde-koehn-18-german-asr,
author = {Benjamin Milde and Arne K{\"o}hn},
title = {Open Source Automatic Speech Recognition for {German}},
booktitle = {Proceedings of ITG 2018},
year = {2018},
address = {Oldenburg, Germany},
pages = {251--255}
}
```

An open access Arxiv preprint is available here: https://arxiv.org/abs/1807.10311 (same content as the ITG version)

You can also additionaly cite our [older paper](https://www.inf.uni-hamburg.de/en/inst/ab/lt/publications/2015-radeck-arnethetal-tsd2015-speechcorpus.pdf), if you like: 

```
@InProceedings{Radeck-Arneth2015,
author = {Radeck-Arneth, Stephan and Milde, Benjamin and Lange, Arvid and Gouvea, Evandro and Radomski, Stefan and M{\"{u}}hlh{\"{a}}user, Max and Biemann, Chris},
booktitle = {Proceedings Text, Speech and Dialogue (TSD)},
title = {{Open Source German Distant Speech Recognition: Corpus and Acoustic Model}},
year = {2015},
address = {Pilsen, Czech Republic},
pages = {480--488}
}
```

If you use our training scripts or models commercially, please mention this repository in your about section, documentation or similar.
