#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 23:25:35 2018
Works best with VM1 and VM2 from https://clarin.phonetik.uni-muenchen.de/BASRepository/

@author: Benjamin Milde
"""


def read_vm_ids(vm_filename, vm_prefix):
    myids = []
    with open(vm_prefix + vm_filename) as vm1_dev:
        for line in vm1_dev:
            myid = line.split()[0]
            myids += [myid]
    return myids
        
replace_rules = {'"s':'ß','"a':'ä','"u':'ü', '"o':'ö', '"A':'Ä','"U':'Ü', '"O':'Ö', '<':'', '>':'', '-$':' ', '$':'' }

def read_par(myids, vm_prefix):
    db = {}
    for myid in myids:
        speaker = myid[:5]
        try:
            with open(vm_prefix + speaker + '/' + myid+'.par') as parfile:
                txt = []
                for line in parfile:
                    if line[-1] == '\n':
                        line = line[:-1]
                    if line[:4] == 'ORT:':
                        word = line.split()[2]
                        #print(word)
                        for rule in replace_rules.items():
                            word = word.replace(rule[0],rule[1])
                        #print(word)
                        if word[0] != ' ':
                            txt.append(word)
                        else:
                            txt.append(word[1:])
                print(txt)
                db[myid] = ' '.join(txt)
        except:
            print('Error opening file:', vm_prefix + speaker + '/' + myid+'.par')
    return db

def create_kaldi(db, folder,  vm_prefix):
    with open(folder + 'text', 'w' ) as text, open(folder + '/utt2spk', 'w' ) as spk2utt, open(folder + '/wav.scp', 'w' ) as wavscp:
        for myid in sorted(list(db.keys())):
            speaker = myid[:5]
            text.write(myid + ' ' + db[myid] + '\n')
            spk2utt.write(myid + ' ' + speaker + '\n')
            wavscp.write("%s sph2pipe -f wav -p %s |\n" % (myid, vm_prefix + speaker + '/' + myid + '.nis'))

#j511a

for vm_prefix, ids_file, data_folder in [
        ('data/wav/VM1/', 'doc/SETS/VM1_DEV', 'data/vm1_dev/'), 
        ('data/wav/VM1/', 'doc/SETS/VM1_TEST', 'data/vm1_test/'), 
        ('data/wav/VM1/', 'doc/SETS/VM1_TRAIN', 'data/vm1_train/'), 
        ('data/wav/VM2/', 'doc/SETS/VM2_DEV', 'data/vm2_dev/'), 
        ('data/wav/VM2/', 'doc/SETS/VM2_TEST', 'data/vm2_test/')
        ]:
    print(vm_prefix, ids_file, data_folder)
    myids = read_vm_ids(ids_file, vm_prefix)
    db = read_par(myids, vm_prefix)
    create_kaldi(db, data_folder, vm_prefix)
