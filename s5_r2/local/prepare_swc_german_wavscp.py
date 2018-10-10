import os
import re
import collections

corpus = 'data/wav/swc/german/'

train_out = 'data/swc_train/'

wav_scp = collections.defaultdict(list)

sox_str = "%s sox %s -t wav -r 16k -b 16 -e signed -c 1 - |"
#print(wav_scp)

def cleanup_str(mystr):
    return mystr.replace('_','-').replace('%','').replace('(','').replace(')','').replace('&','and').replace('!','').replace('BMW-507','BMW-fuenfnullsieben').replace('…','').replace('daß','dass').replace('2½','zwei ein halb ').replace('–','').replace('/','').replace(' ’ ',' ').replace('°C','Grad Celsius')

def cleanup_file(myfile):
    with open(myfile) as infile:
        filestr = infile.read()
    with open(myfile,'w') as outfile:
        outfile.write(cleanup_str(filestr))

cleanup_file('data/swc_train/segments')
cleanup_file('data/swc_train/text')

segment_ids = {}
utterance_ids = {}

utterance_ids_text = {}

with open('data/swc_train/segments') as segments, open('data/swc_train/utt2spk','w') as uttspk:
    for line in segments:
        split = line.split()
        if not split[0].replace('-','').isalnum():
            print('id not alphanumeric:',split[0])
        if not split[0][:len(split[1])] == split[1]:
            print('id not prefix of utterance')

        segment_id = split[1]

        if segment_id not in segment_ids:
            segment_ids[segment_id] = 1

        utterance_id = split[0]

        if utterance_id not in utterance_ids:
            utterance_ids[utterance_id] = 1
            uttspk.write(utterance_id + ' ' + segment_id + '\n')
        else:
            print('warning duplicate id in segments:',utterance_id)

print(utterance_ids_text)
with open('data/swc_train/text') as text:
    for line in text:
        split = line.split()
        print(line)
        if split[0] not in utterance_ids:
            print('erronous id in text:', split[0])
        if split[0] not in utterance_ids_text:
            utterance_ids_text[split[0]] = 1
        else:
            print('warning duplicate id in text:',utterance_id)

    print('Length text ids:',len(utterance_ids_text.keys()) , 'length ids' ,len(utterance_ids.keys()))
    print('Difference of ids:', set(utterance_ids_text.keys()) - set(utterance_ids.keys()))

#now creating wav.scp
for folder in os.listdir(corpus):
    try:
        for f in os.listdir(os.path.join(corpus, folder)):
            if re.fullmatch("audio[0-9]?\.ogg", f):
                wav_scp[folder] += [os.path.join(corpus, folder, f)]
    except:
        None
        #print('Not a folder: ', folder)

with open('data/swc_train/wav.scp','w') as wavscp: 
    for key in sorted(list(wav_scp.keys())):
        audio_str = ' '.join(sorted(list(wav_scp[key])))
        cleaned_key = cleanup_str(key)
        if cleaned_key in segment_ids:
            wavscp.write(sox_str % (cleanup_str(key),audio_str) + '\n')
