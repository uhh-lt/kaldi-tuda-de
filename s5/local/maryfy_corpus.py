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

import common_utils
import argparse
import codecs
import multiprocessing
import maryclient
import subprocess
import time

import RemoteException

from functools import partial

from multiprocessing import Pool

ignore_lines = ['<','#']
buffer_size = 500

@RemoteException.showError
def processLine(line,mary,scriptpath):
    #http://stackoverflow.com/questions/10190981/get-a-unique-id-for-worker-in-python-multiprocessing-pool
    tokens = []
    try:
        proc_num = multiprocessing.current_process()._identity[0]-1
        tokens,phonemes = common_utils.getCleanTokensAndPhonemes(line,mary,proc_num)
    except Exception as err:
        print '[',proc_num,']','Error, omitting', line
        print err
        if scriptpath != '' and ('Read timed out' in str(err)):
            print 'restarting maryServer'
            restartMaryServer(scriptpath,None)
    return ' '.join(tokens)

def processBuffer(workerpool,mary,mybuffer,outfile,scriptpath):
    func = partial(processLine, mary=mary,scriptpath=scriptpath)
    sentences = workerpool.map(func, mybuffer)
    for sentence in sentences:
        if sentence != '':
            outputfile.write(sentence+'\n')

def startMaryServer(scriptpath):
    maryproc=subprocess.Popen(['bash', scriptpath], stdout=subprocess.PIPE)
    time.sleep(5.0)
    return maryproc

def restartMaryServer(scriptpath,maryproc):
    #maryproc.terminate()
    #maryproc.kill()
    proc=subprocess.Popen(['killall','-9','java'], stdout=subprocess.PIPE)
    time.sleep(1.0)
    return startMaryServer(scriptpath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares a German text corpus, each sentence on a new line, with MARYs TTS frontend.')
    parser.add_argument('-i', '--input', dest='input', help='Input corpus file', type=str, default = '')
    parser.add_argument('-o', '--output', dest='output', help='Output corpus file', type=str, default='')
    parser.add_argument('-p', '--num-proc', dest='num_proc', help='Number of processes to use for MARYs TTS server', type=int, default=1)
    parser.add_argument('-s', '--skip', dest='skip_lines', help='Skip this number of lines in the input file', type=int, default=0)
    parser.add_argument('-a', '--append', dest='append', help='Skip this number of lines in the input file', action='store_true')

    parser.add_argument('-m', '--mary', dest='mary', help='Run MARY TTS server with this script', type=str, default='')

    args = parser.parse_args()

    assert(args.input != args.output)

    workerpool = Pool(processes=args.num_proc)
    mary = maryclient.maryclient(2*args.num_proc)
    print 'Reserved',args.num_proc,'processes.'
    print 'Input file:',args.input,'output file:',args.output
    
    outfile_opt = 'w'

    if args.append:
        outfile_opt = 'a'
        print 'appending to output file.'

    if args.skip_lines > 0:
        print "I'm skipping the first",args.skip_lines,"of the input file"

    scriptpath = args.mary

    if scriptpath != '':
        print 'starting mary server...'
        maryproc = startMaryServer(scriptpath)

    with codecs.open(args.input,'r','utf-8') as inputfile, codecs.open(args.output,'w','utf-8') as outputfile:
        lineno = 0
        mybuffer = []
        for line in inputfile:
            if any([line.startswith(elem) for elem in ignore_lines]):
                continue
            if lineno >= args.skip_lines:
                mybuffer.append(line)
            lineno += 1
            if(lineno % buffer_size == 0 and len(mybuffer)>0):
                processBuffer(workerpool,mary,mybuffer,outputfile,scriptpath)
                del mybuffer
                mybuffer = []
                print 'Processed:',lineno,'lines.'

            if scriptpath != '':
                #restart mary tts every 10000 requests
                if(lineno % 20000 == 0):
                    maryproc = restartMaryServer(scriptpath,maryproc)                

        #process any outstanding elements        
        if len(mybuffer)>0:
            processBuffer(workerpool,mary,mybuffer,outputfile,scriptpath)
