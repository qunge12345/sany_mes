import sys
sys.path.append("..")

import utils
import json
import threading
from ctypes import *
from enum import Enum, unique
from xd_event import *

@unique
class ReplyTaskStatus(Enum):
    WAIT = 0
    SUCCESS = 1
    FAILED = 2
    EXECUTING = 3
    GRASPING = 4

class Replyer(object):
    '''
    reply by soap
    '''
    soaplib = cdll.LoadLibrary("./GSoapDllx86.dll")
    soapLock = threading.Lock()
    log = utils.logger().getLogger('replyer')

    @staticmethod
    def typicalSend(evt, ts = ReplyTaskStatus.WAIT):
        '''
        send back to light-isolation
        '''
        url = b''
        data = rb''

        if evt.getEventSource() == '0': # xiongdi device

            info = (evt.getMachineStatus(), evt.getMachineInfo(), str(ts.value), evt.getMachineName(), evt.getMachineIP(), evt.getEventSource())
            data = rb'{"data":"{\"event_id\":\"%s\",\"event_info\":\"%s\",\"event_status\":\"%s\",\"machine_code\":\"%s\",\"machine_ip\":\"%s\"}","id" :"","type" : "%s"}' % \
            (tuple(map(lambda x: x.encode('utf-8'), info)))

            url = b"http://192.168.2.30:8733/TraQRCodeService?wsdl"

        elif evt.getEventSource() == '1': # hang xin device

            info = (evt.getToken(), evt.getMachineStatus(), evt.getMachineInfo(), str(ts.value), evt.getMachineName(), evt.getMachineIP(), evt.getEventSource())
            data = rb'{"data":"{\"token\":\"%s\",\"event_id\":\"%s\",\"event_info\":\"%s\",\"event_status\":\"%s\",\"machine_code\":\"%s\",\"machine_ip\":\"%s\"}","id" :"","type" : "%s"}' % \
            (tuple(map(lambda x: x.encode('utf-8'), info)))
            
            url = b"http://192.168.2.50:8733/TraQRCodeService?wsdl"
        else:
            Replyer.log.info('UNKNOWN event, replyer will send nothing')
            return

        Replyer.soapLock.acquire()
        try:
            Replyer.log.info("send to light isolation: " + data.decode())
            ret = Replyer.soaplib.func_send_data(data, url)
            # print(ret)
        except Exception as e:
            Replyer.log.error(e)
        finally:
            Replyer.soapLock.release()