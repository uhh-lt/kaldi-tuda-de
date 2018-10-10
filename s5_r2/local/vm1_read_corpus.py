#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 23:25:35 2018

@author: Benjamin Milde
"""


def read_vm_ids(vm_filename, vm_prefix='data/wav/VM1/'):
    myids = []
    with open(vm_prefix + vm_filename) as vm1_dev:
        for line in vm1_dev:
            myid = line.split()[0]
            myids += [myid]
    return myids
        
replace_rules = {'"s':'ß','"a':'ä','"u':'ü', '"o':'ö', '"A':'Ä','"U':'Ü', '"O':'Ö', '<':'', '>':'', '-$':' ', '$':'' }

def read_par(myids, vm_prefix='data/wav/VM1/'):
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

def create_kaldi(db, folder,  vm_prefix='data/wav/VM1/'):
    with open(folder + '/text', 'w' ) as text, open(folder + '/utt2spk', 'w' ) as spk2utt, open(folder + '/wav.scp', 'w' ) as wavscp:
        for myid in sorted(list(db.keys())):
            speaker = myid[:5]
            text.write(myid + ' ' + db[myid] + '\n')
            spk2utt.write(myid + ' ' + speaker + '\n')
            wavscp.write("%s sph2pipe -f wav -p %s |\n" % (myid, vm_prefix + speaker + '/' + myid + '.nis'))

#j511a

for ids_file, data_folder in [('doc/SETS/VM1_DEV', 'data/vm1_dev/'), ('doc/SETS/VM1_TEST', 'data/vm1_test/'), ('doc/SETS/VM1_TRAIN', 'data/vm1_train/'), ('doc/SETS/VM2_DEV', 'data/vm2_dev/'), ('doc/SETS/VM2_TEST', 'data/vm2_test/')]:
    print(ids_file, data_folder)
    myids = read_vm_ids(ids_file)
    db = read_par(myids)
    create_kaldi(db, data_folder, vm_prefix='data/wav/VM1/')
