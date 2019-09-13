# -*- coding: utf-8 -*-

# Copyright 2018 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
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

from __future__ import print_function

import argparse
import io
from math import fsum

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shows the length (in hours) of a Kaldi folder. Either the segment file or the utt2dur file needs to be present.')
    parser.add_argument('-f', '--folder', dest='folder', help='The kaldi folder for which the length (in hours) should be calculated', type=str, default='')

    args = parser.parse_args()

    if args.folder == '':
      print('You have to specify a Kaldi data folder with the -f flag.')
   
    folder = args.folder

    if folder[-1] != '/':
      folder += '/'

    try:
      with io.open(folder + 'utt2dur') as utt2dur:
        sum_list = []
        for line in utt2dur:
          if line[-1]=='\n':
            line = line[:-1]
          sum_list += [float(line.split()[1])]
        hours = fsum(sum_list) / 60.0 / 60.0
        print('Utt2dur file: ', args.folder, 'is', hours, ' hours!')
    except:
      print('Could not open/process utt2dur file in:', args.folder)


    try:
      with io.open(folder + 'segments') as segments:
        sum_list = []
        for line in segments:
          diff = float(line.split()[3]) - float(line.split()[2])
          sum_list += [diff]
          if diff > 2000:
            print('Warning over-long segment:', diff)
            print(line)
          if float(line.split()[2]) > float(line.split()[3]):
            print('Warning, end marker before start:', line)
          elif float(line.split()[2]) == float(line.split()[3]):
            print('Warning, end marker == start marker:', line)
        hours = fsum(sum_list) / 60.0 / 60.0

        print('Segment file: ', args.folder, 'is', hours, ' hours!')
    except:
      print('Could not open/process segments file in:', args.folder)
