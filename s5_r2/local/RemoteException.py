#  The MIT License (MIT)
#
#  Copyright (c) 2014 Nicco Kunzmann
#
#  https://gist.github.com/niccokunzmann/5763860
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import sys
import traceback
import StringIO

from copy_reg import dispatch_table, pickle

def exc_info(hide_calls = 0):
    '''as sys.exc_info() but returns a remote exception object'''
    ErrorType, thrownError, traceback = sys.exc_info()
    for i in range(hide_calls):
        if traceback.tb_next:
            traceback = traceback.tb_next
    err = withTracebackPrint(ErrorType, thrownError, traceback)
    return type(err), err, traceback

def withTracebackPrint(ErrorType, thrownError, _traceback):
    '''returns an Exception object for the given ErrorType of the thrownError and the _traceback can be used like withTracebackPrint(*sys.exc_info())'''
    file = StringIO.StringIO()
    traceback.print_exception(ErrorType, thrownError, _traceback, file = file)
    return _loadError(ErrorType, thrownError, file.getvalue())
    ## why don't we just use the following line?
    ## return ErrorType(file.getvalue())
    ## because the arguments would get hurt
    ## or the traceback print has no unescaped newlines

class _RemoteExceptionMeta(type):
    'Metaclass for RemoteExceptions to make copy_reg accept them'
    pass
                    
def _pickle_function(RemoteExceptionClass):
    'how to pickle the remote exception type'
    return asRemoteException, (RemoteExceptionClass.BaseExceptionType,)

pickle(_RemoteExceptionMeta, _pickle_function)

_remoteExceptionCache = {} # exception : RemoteException

def _newRemoteException(ErrorType):
    '''create a new RemoteExceptionType from a given errortype'''
    RemoteErrorBaseType = _RemoteExceptionMeta('', (ErrorType,), {})
    class RemoteException(RemoteErrorBaseType):
        BaseExceptionType = ErrorType
        
        def __init__(self, thrownError, tracebackString):
            self.thrownError = thrownError
            self.tracebackString = tracebackString
            RemoteErrorBaseType.__init__(self, *thrownError.args)
            
        loadError = staticmethod(_loadError)
        
        def __str__(self):
            return '\n%s\n%s' % (self.tracebackString, self.thrownError)

        def __reduce__(self):
            args = (ErrorType, self.thrownError, self.tracebackString)
            return self.loadError, args
    RemoteException.__name__ = 'Remote' + ErrorType.__name__
    return RemoteException


def asRemoteException(ErrorType):
    '''return the remote exception version of the error above
you can catch errors as usally:
>>> try:
raise asRemoteException(ValueError)
except ValueError:
pass
or you can catch the remote Exception
>>> try:
raise asRemoteException(ReferenceError)(ReferenceError(),'')
except asRemoteException(ReferenceError):
pass
'''
    RemoteException = _remoteExceptionCache.get(ErrorType)
    if RemoteException is None:
        RemoteException = _newRemoteException(ErrorType)
        _remoteExceptionCache.setdefault(ErrorType, RemoteException)
        _remoteExceptionCache.setdefault(RemoteException, RemoteException)
        return _remoteExceptionCache.get(ErrorType)
    return RemoteException

def _loadError(ErrorType, thrownError, tracebackString):
    '''constructor of RemoteExceptions'''
    RemoteException = asRemoteException(ErrorType)
    return RemoteException(thrownError, tracebackString)

def showError(function):
    def functionShowingTheError(*args, **kw):
        try:
            return function(*args, **kw)
        except:
            type, error, traceback = exc_info(1)
            raise type, error, traceback
    functionShowingTheError.__name__ = function.__name__
    functionShowingTheError.__module__ = function.__module__
    return functionShowingTheError

@showError
def _testError():
    raise ValueError('Exception!')

def _test_no_error():
    return 12

if __name__ == '__main__':
    import multiprocessing
    p = multiprocessing.Pool(processes = 2)
    r = p.apply_async(_testError)
    print(r.get(1))
    
__all__ = ['withTracebackPrint', 'asRemoteException', 'exc_info', 'showError']
