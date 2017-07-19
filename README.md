# Open source distant speech recognition recipe and corpus for building German acoustic models with Kaldi
This recipe and collection of scripts enables you to train large vocabulary German acoustic models for distant speech recognition (DSR) in a speaker-independent speech recognition setting with [Kaldi](http://kaldi.sourceforge.net/). State-of-the-art modelling techniques include SGMM models and DNN-HMM models. The speech corpus has been recorded using a Microsoft Kinect and two other microphones in parallel at Technische Universität Darmstadt and has been released under a permissive license [(CC-BY 4.0)](http://creativecommons.org/licenses/by/4.0/). The corpus compromises ~31h of training data per microphone and ~5h separated into development and test partitions. The speech data has been recorded using the [KisRecord software](http://kisrecord.sourceforge.net/).

The current recipe trains and tests exclusively on the training and test partitions of the Microsoft Kinect beamformed and noise reduced audio data. There is also data for three other microphones.

The scripts will ask you where to place larger files and can download all necessary files (speech corpus, German texts, phoneme dictionaries) to train the acoustic and language models. You can also download these resources manually, see Section "Getting data files separately" down below.

## Prerequisites

The scripts are only tested under Linux (Ubuntu 14.04). Download and install Kaldi and follow the installation instructions. You can download a recent version using git:

```
 git clone https://github.com/kaldi-asr/kaldi.git kaldi-trunk --origin golden
```

In Kaldi trunk:

1. go to tools/  and follow INSTALL instructions there.

   *Optional:* If you have some extra time, it can make sense to use a newer [development version of ATLAS](http://sourceforge.net/projects/math-atlas/files/Developer%20%28unstable%29/) instead of the one supplied by your distribution, as the newer versions tend to be much faster and can make use of AVX instructions if you have a newer processor. It takes up to a day to build though and cannot be parallelized (using -j with make will produce a ATALS library which will most likely produce incorrect results or crash randomly).

2. go to src/ and follow INSTALL instructions there.

**Our scripts are meant to be placed into its own directory in KALDIs egs/ directory.** This is also where all the other recipes reside in. If you want to build DNN models, you probably want to enable CUDA in KALDI with the configure script in src/. You should have a relatively recent Nvidia GPU, at least one with the Kepler architecture.

You also need [MARY 5.1.1](https://github.com/marytts/marytts/releases/download/v5.1.1/marytts-5.1.1.zip) running on your local machine. Please use this exact version, as other versions e.g. 5.1.2 are known to be uncompatible with our scripts currently. Start the MARY server before running our scripts. It will be used to generate phoneme entries in the phoneme dictionary for OOV words. It was also used to automatically clean the texts for the LM, but you will only need to do this more compute intensive step if you want to extend the LM, as we have packaged preprocessed and MARY-fied texts (8 million sentences) that are automatically downloaded.

You will also need Python 2.7.x installed on your system with a recent version of the requests package (http://docs.python-requests.org/en/latest/). To install it, either run "pip install requests" for a system-wide installation or "pip install --user requests" if you don't have admin privileges.

## Building the acoustic models

After you have installed the prerequisites, edit cmd.sh in the s5/ directory of this distribution to adjust for the number of processors you have locally (change nJobs and nDecodeJobs accordingly). You could probably also uncomment the cluster configuration and run the scripts on a cluster, but this is untested and may require some tinkering to get it running.

Then, simply run ./run.sh in s5/ to build the acoustic and language models. The script will ask you where to place larger files (feature vectors and KALDI models) and automatically build appropriate symlinks. [Kaldi_lm](http://www.danielpovey.com/files/kaldi/kaldi_lm.tar.gz) is automatically downloaded and compiled if it is not found on your system and standard Kneser-Ney is used for a 3-gram LM.

## Getting data files separately

You can of course also use and download our data resources separately.

### Speech corpus

The corpus can be downloaded [here](http://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/german-speechdata-package-v2.tar.gz). The license is [CC-BY 4.0](http://creativecommons.org/licenses/by/4.0/).
The run.sh script expects to find the corpus data extracted in data/wav/ and will download it for you automatically, if it does not find the data.

### German language texts

Preprocessed read sentences from the [German Wikipedia](https://de.wikipedia.org/), the [European Parliament Proceedings Parallel Corpus](http://www.statmt.org/europarl/) and a crawled corpus of direct speech can be found [here](http://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/German_sentences_8mil_filtered_maryfied.txt.gz)
 
The scripts expect to find one gzipped text file containing all the sentences (each on its own line) in data/local/lm/cleaned.gz

The preproccesing with [MARY](http://mary.dfki.de/) canonicalizes numbers, literals and abbreviations and removes all punctuation. E.g. 51 is changed into "einundfünfzig". Spelling is currently not canonicalized, but rules to translate from old German spellings (pre-1996 and pre-2004/06) are planned for a later release.

If you want to preprocess your own texts, you can use s5/local/maryfy_corpus.py.

```
python s5/local/maryfy_corpus.py --help
```

should point you into the right direction. You need to supply the path of the MARY server start script. MARY will unfortunately have problems if you try to process millions of lines of text in one go and it might become unresponsive with all its processing threads being stuck in endless loops. The current quick hack implemented in maryfy_corpus.py will routinely call "killall java" and then restart MARY. This of course only works, if you have no other Java programs running under your username besides MARY. 

### German phoneme dictionary

The phoneme dictionary is currently not supplied with this distribution, but the scripts to generate them are. DFKIs MARY includes a nice [LGPL German phoneme dictionary](https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt) with ~36k entries. Other sources for phoneme dictionary entries can be found at [BAS](ftp://ftp.bas.uni-muenchen.de/pub/BAS). Our parser understands the different formats of     [VM.German.Wordforms](ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/VM.German.Wordforms), [RVG1_read.lex](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_read.lex), [RVG1_trl.lex](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_trl.lex) and [LEXICON.TBL](ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG-J/LEXICON.TBL).
The final dictionary covers ~44.8k unique German words with 70k entries total (pronunciation variants). You can also disable the BAS dictionaties, if it is important for to have a phoneme dictionary with an open license. You will then have a lexicon with ~36k unique German words and no pronounciation variants.

build_big_lexicon.py can import many dictionaries in the [BasSAMPA](http://www.bas.uni-muenchen.de/Bas/BasSAMPA)  format and merge them into a single dictionary. Its parser understand many variants and dialects of BasSAMPA and the adhoc dictionary formats. To support new variants you'll have to edit def guessImportFunc(filename). The output is a serialised python object.

export_lexicon.py will export such a serialised python dictionary into KALDIs [lexion_p.txt](http://kaldi.sourceforge.net/data_prep.html#data_prep_lang_creating) format (this allows to model different phonetic realisations of the same word with probabilities). Stress markers in the phoneme set are grouped with their unstressed equivalents in KALDI using the extra_questions.txt file. It is also possible to generate a CMU Sphinx formated dictionary with the same data using the -spx option. The Sphinx format also allows pronunciation variants, but cannot model probabilities for these variants.

See also:
```
python s5/local/build_big_lexicon.py --help
python s5/local/export_lexicon.py --help
```
