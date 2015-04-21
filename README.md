# Open source distant speech recipe for building German acoustic models with KALDI
The speech corpus has been recorded using a Microsoft Kinect and three other microphones in parallel at Technische Universität Darmstadt. The corpus compromises ~31h of training data per microphone and 5h seperated into development and test partitions. The speech data has been recorded using the [KisRecord software](http://kisrecord.sourceforge.net/)

The current recipe trains and tests exlusively on the training and test partitions of the Microsoft Kinect beamformed and noise reduced audio data.

The scripts will ask you where to place larger files and can download all neccesary files (audio, German texts, phoneme dictionary) to train the acoustic and language models. 

## Prerequsites

The scripts are only tested under Linux (Ubuntu 14.04). Download and install KALDI and follow the installation instructions. You can download a recent version using svn:

```
svn co https://svn.code.sf.net/p/kaldi/code/trunk kaldi-trunk
```

In KALDI trunk:
(1) go to tools/  and follow INSTALL instructions there.
If you have some extra time, it can make sense to use a newer [development version of ATLAS](http://sourceforge.net/projects/math-atlas/files/Developer%20%28unstable%29/) instead of the one supplied by your distribution, as the newer version tend to be much faster and can make use of AVX instructions if you have a newer processor. It takes up to a day to build though and cannot be parallized (using -j with make will produce a ATALS library which will most likely produce incorrect results or crash randomly).
(2) go to src/ and follow INSTALL instructions there.

*Our scripts are meant to be placed into its own directory in KALDIs egs/ directory.* This is also where all the other recipes reside in. If you want to build DNN models, you need to enable CUDA in KALDI with the configure script in src/.

You also need MARY 5.1.1 running on your local machine (https://github.com/marytts/marytts/releases/download/v5.1.1/marytts-5.1.1.zip). Please use this version, as other versions e.g. 5.1.2 are known to be uncompatible with these scripts currently. Start the MARY server before running our scripts. It will be used to generate phoneme entries in the phoneme dictionary for OOV words. It was also used to automatically clean the texts for the LM, but you will only need to do this more compute intensive step if you want to extend the LM, as we have packaged preprocessed texts (8 million sentences) that are automatically downloaded.

You need python 2.7.x installed on your system with a recent version of the requests package (http://docs.python-requests.org/en/latest/). To install it, either run "pip install requests" for a system-wide installation or "pip install --user requests" if you don't have admin priviledges.

## Building 

After you have fullfilled the prerequsites, simply run run.sh to build the acoustic and language models. Kaldi_lm is automatically downloaded and compiled if it is not found on your system.
