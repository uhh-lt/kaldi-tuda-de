# This script builds the folder structure needed to train the model. It also asks where bigger files (mfcc, lm, exp)

# Copyright 2015 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common_utils import make_sure_path_exists
import os
import sys

if not os.path.exists('run.sh'):
    print 'You have to run this python script from the base dir, where run.sh is located. WARNING: aborting.'
    sys.exit('wrong woring directory')

print 'Creating data dir(s)...'
make_sure_path_exists('data/lexicon/')
make_sure_path_exists('data/local/')
make_sure_path_exists('data/local/dict/')
make_sure_path_exists('data/local/lang/')
make_sure_path_exists('data/local/lm/')
make_sure_path_exists('data/local/lm/3gram-mincount/')

#if exp and mfcc don't exist locally, create them as link to some other directory on a larger disk
if not os.path.exists('exp/') and not os.path.exists('mfcc/'):
    default_dir = '/srv/data/speech/tuda_kaldi_de/'
    data_dir = raw_input('Where do you want to store mfcc vectors and models (exp)? It should point to some largish disk. default: ' + default_dir) 
    if data_dir == '':
        data_dir = default_dir

    if data_dir.endswith('/'):
        data_dir = data_dir[:-1]

    mfcc_dir_src = data_dir + '/mfcc/'
    exp_dir_src = data_dir + '/exp/'

    print 'Mfcc source dir: ',mfcc_dir_src,' model (exp) dir: ', exp_dir_src

    make_sure_path_exists(mfcc_dir_src)
    make_sure_path_exists(exp_dir_src)

    os.symlink(mfcc_dir_src,'./mfcc')
    os.symlink(exp_dir_src,'./exp')

