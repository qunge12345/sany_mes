import os   
import logging
import logging.handlers
import inspect
import socket
import time
import traceback

class Singleton(object):
    """singleton class
    """
    _instance = None
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)  
        return cls._instance

class logger(Singleton):
    """singleton class logger
    """
    logger_initialized = False

    def __init__(self):
        if False == logger.logger_initialized:
            this_file = inspect.getfile(inspect.currentframe())
            dirpath = os.path.abspath(os.path.dirname(this_file))
            dirpath = os.path.join(dirpath, 'log')
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            elif not os.path.isdir(dirpath):
                os.remove(dirpath)
                os.makedirs(dirpath)
            logging.basicConfig(level=logging.INFO,  
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',  
                        # filename=os.path.join(dirpath, "MES-SANYI_" + time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time())) + ".log"),  
                        filemode='w') 
                        
            ## make a Handler to sys.stderr
            # console = logging.StreamHandler()
            # console.setLevel(logging.INFO)
            # # set format
            # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            # console.setFormatter(formatter)
            # # add console handler to root logger
            # logging.getLogger('').addHandler(console)

            # rotating handler
            # rHandler = logging.handlers.RotatingFileHandler(filename = os.path.join(dirpath, "MES-SANYI_RT.log"), maxBytes = 1 * 1024 * 1024, backupCount = 5) # 1M
            rHandler = logging.handlers.TimedRotatingFileHandler(filename = os.path.join(dirpath, "MES-SANYI_RT.log"), when = 'S', interval = 3600, backupCount = 100)  # 3600 seconds == 1 hours
            rHandler.suffix = '%Y-%m-%d_%H-%M-%S' + ".log"
            rHandler.setLevel(logging.INFO)
            rFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            rHandler.setFormatter(rFormatter)
            logging.getLogger('').addHandler(rHandler)

            logger.logger_initialized = True

    def getLogger(self, name='servicelog'):
        if not isinstance(name, str):
            raise TypeError('logger name must be a string')
        # print('create logger \'' + name + '\' at time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        return logging.getLogger(name)

# field func decorator: catch exception
def mb_default_catch_exception(origin_func):
    def wrapper(self, *args, **kwargs):
        try:
            return origin_func(self, *args, **kwargs)
        except Exception as e:
            # self._log.error(traceback.format_exc())
            self._log.error(e)
    return wrapper

def mb_lock_and_catch(origin_func):
    def wrapper(self, *args, **kwargs):
        self._lock.acquire()
        try:
            return origin_func(self, *args, **kwargs)
        except Exception as e:
            self._log.error(traceback.format_exc())
            self._log.error(e)
        finally:
            self._lock.release()
    return wrapper

def checkKeyExistAndType(dic, key, type):
    if not isinstance(dic, dict):
        return False, 'the container is not a dict'
    elif key not in dic:
        return False, '%s is missing ' % key
    elif not isinstance(dic[key], type):
        return False, 'param %s is not a %s' % (key, str(type))
    return True, ''

def getAllDataWithTimeout(sock, dataLen, timeout = None):
    leftLen = dataLen
    sock.settimeout(timeout)
    data = bytearray()
    while leftLen > 0:
        recvLen = leftLen
        if recvLen > 4096:
            recvLen = 4096
        tempdata = sock.recv(recvLen)
        tempDataLen = len(tempdata)
        if 0 == tempDataLen:
            return b''
        data.extend(tempdata)
        leftLen -= tempDataLen
    return data

def exeShellWithOutput(cmd, loger=None):
    if None == loger:
        loger = logger().getLogger('undefine logger')
    try:
        loger.info('call shell command: ' + cmd)
        result = os.popen(cmd)  
        res = result.read()
        for line in res.splitlines():
            if line is not '':
                loger.info(line)
        result.close()
    except BaseException as e:
        loger.critical(e)
    loger.info('call shell command over')

def main():
    exeShellWithOutput("echo aaa")
    exeShellWithOutput("echo bbb")
    exeShellWithOutput("echo ccc")
    pass

if __name__ == '__main__':
    main()
