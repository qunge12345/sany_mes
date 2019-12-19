import sys
sys.path.append("..")

import utils
import json
import threading
from ctypes import *
from enum import Enum, unique
from xd_event import *
import requests

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
    
    @staticmethod
    def sendMessageToLightIsolation(data):
        url = b"http://192.168.2.30:8733/TraQRCodeService?wsdl"
        Replyer.soapLock.acquire()
        try:
            # Replyer.log.info("send: " + data)
            sdata = rb'{"data":"%s","id":"","type":"2"}' % data.replace('"',r'\"').encode('utf-8')
            ret = Replyer.soaplib.func_send_data(sdata, url)
        except Exception as e:
            Replyer.log.error(e)
        finally:
            Replyer.soapLock.release()

    @staticmethod
    def sendMessage(data):
        msgT = json.loads(data).get('msgT', 1)
        if (msgT == 1):
            url = b'http://localhost:8082/api/saveRobotInfo'
        else:
            url = b'http://localhost:8082/api/saveRobotRealInfo'
        postData = data.encode('utf-8')
        Replyer.log.info('POST to ' + url.decode())
        Replyer.log.info('DATA is ' + postData.decode())
        try:
            req = requests.post(url = url, data = postData, timeout = 1.0)
            Replyer.log.info('Response code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))
        except Exception as e:
            Replyer.log.error(e)

if __name__ == '__main__':
    d1 = XDEvent('{         \
    "event_source":"0",\
    "event_status":"0",\
    "info": "1:0",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "5",\
    "time": "20180404095212",\
    "token":"asdfasdf",\
    "version": "1.0"\
    }')

    # Replyer.typicalSend(d1, ReplyTaskStatus.WAIT)
    Replyer.sendMessage(json.dumps({'aaa':'bbb','ccc':2}))