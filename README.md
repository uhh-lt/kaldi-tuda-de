# Open source distant speech recipe for building German acoustic models with KALDI
The speech corpus has been recorded using a Microsoft Kinect and three other microphones in parallel at Technische Universität Darmstadt. The corpus compromises ~31h of training data per microphone and 5h seperated into development and test partitions. The speech data has been recorded using the KisRecord software (http://kisrecord.sourceforge.net/)

The current recipe trains and tests exlusively on the training and test partitions of the Microsoft Kinect beamformed and noise reduced audio data.

The scripts will ask you where to place larger files and can download all neccesary files (Audio, German texts, Phoneme dictionary) to train the acoustic and language models. 

## Prerequsites

Download and install KALDI and follow the installation instructions on http://kaldi.sourceforge.net/. Our scripts are meant to be placed into KALDIs egs directory. If you want to build DNN models, you need to enable CUDA in KALDI.

You also need MARY 5.1.1 running on your local machine (https://github.com/marytts/marytts/releases/download/v5.1.1/marytts-5.1.1.zip). Please use this version, as other versions e.g. 5.1.2 are known to be uncompatible with these scripts currently. Start the MARY server before running our scripts. It will be used to generate phoneme entries in the phoneme dictionary for OOV words. It was also used to automatically clean the texts for the LM, but you will only need to do this more compute intensive step if you want to extend the LM, as we have packaged preprocessed texts (8 million sentences) that are automatically downloaded.

## Building 

After you have fullfilled the prerequsites, simply run run.sh to build the acoustic and language models. Kaldi_lm is automatically downloaded and compiled if it is not found on your system.
