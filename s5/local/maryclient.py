#!/usr/bin/env python

# -*- coding: utf-8 -*- 

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

import requests
import StringIO

import ctypes
import sys
import traceback

#
# A simple MARY TTS client (5.x) in Python, only generates intermidate MARY TTS phoneme format. 
# This class reuses connections with the request framework (esp. helpful for bulk processing), but you have to install it:
# pip install requests
# 
# Try http://mary.dfki.de:59125/ with a sentence of your choice and set OUTPUT TYPE to 
#

class maryclient:

    def __init__(self, connections = 2):

        self.host = '127.0.0.1'
        self.port = 59125
        self.input_type = 'TEXT'
        self.output_type = 'PHONEMES'
        self.audio = 'WAVE_FILE'
        self.locale = 'de'
        self.voice = ''

        self.reserve(connections)

    def reserve(self,num_conn):
        self.connection_pool = [requests.Session() for x in xrange(num_conn)]

    def generate(self, message, connection_pool_num=0):
        '''Sends the text string in message to the MARY server and 
           format.'''
        assert(len(self.connection_pool) > connection_pool_num)
        
        params = {'INPUT_TEXT': message.encode('utf-8'),
                'INPUT_TYPE': self.input_type,
                'OUTPUT_TYPE': self.output_type,
                'LOCALE': self.locale
                #'AUDIO': self.audio,
                #'VOICE': self.voice,
                }
        r = self.connection_pool[connection_pool_num].post('http://'+self.host+':'+str(self.port)+'/process',data=params,timeout=(10.0,10.0))
        
        if r.status_code != requests.codes.ok:
            raise RuntimeError('error in http request:'+str(r.status_code))
        
        returnbuffer = r.text
        return returnbuffer
