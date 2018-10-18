
import sys
sys.path.append("..")

import utils
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from event_processor import EventProcessor
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

class CommunicationTerminal(BaseHTTPRequestHandler):
    '''
    communicate with XiongDi devices
    '''
    soaplib = cdll.LoadLibrary("./GSoapDllx86.dll")
    soapLock = threading.Lock()
    log = utils.logger().getLogger('communication terminal')

    @staticmethod
    def setEventProcessor(eventProcessor):
        CommunicationTerminal.evtProc = eventProcessor

    def do_POST(self):
        data = self.rfile.read(int(self.headers["content-length"])).decode('utf-8')
        CommunicationTerminal.log.info('http receive: ' + data)
        # response
        self.send_response(200)
        self.end_headers()
        # push the message to event processor
        CommunicationTerminal.evtProc.pushMessage(data)

    @staticmethod
    def startServer():
        st = threading.Thread(target = CommunicationTerminal.listenHandler, name = 'http server' , args = ())
        st.setDaemon(True)
        st.start()
    
    @staticmethod
    def listenHandler():
        httpd = HTTPServer(('0.0.0.0', 8080), CommunicationTerminal)
        CommunicationTerminal.log.info("HTTP Server started")
        httpd.serve_forever()


    @staticmethod
    def typicalSend(evt, ts = ReplyTaskStatus.WAIT):
        info = (evt.getMachineStatus(), evt.getMachineInfo(), str(ts.value), evt.getMachineName(), evt.getMachineIP(), evt.getEventSource())
        data = rb'{"data":"{\"event_id\":\"%s\",\"event_info\":\"%s\",\"event_status\":\"%s\",\"machine_code\":\"%s\",\"machine_ip\":\"%s\"}","id" :"","type" : "%s"}' % \
        (tuple(map(lambda x: x.encode('utf-8'), info)))

        # xiong di device
        url = b"http://192.168.2.30:8733/TraQRCodeService?wsdl"

        if evt.getEventSource() == '1': # hang xin device
            url = b"http://192.168.2.30:8733/TraQRCodeService?wsdl"

        CommunicationTerminal.soapLock.acquire()
        try:
            ret = CommunicationTerminal.soaplib.func_send_data(data, url)
            # print(ret)
        except Exception as e:
            CommunicationTerminal.log.error(e)
        finally:
            CommunicationTerminal.soapLock.release()


if __name__ == '__main__':
    # import time
    CommunicationTerminal.setEventProcessor("i'm wrong")
    # CommunicationTerminal.startServer()
    # while True:
    #     time.sleep(1)
    # m = 222
    # t = rb'{"data":"{\"event_id\":\"%s\",\"event_info\":\"\",\"ip\":\"192.168.1.12\"}","id" :"","type" : "1"}' % str(m).encode('utf-8')
    # print(t)
    de = XDEvent('{         \
    "event_source":"0",\
    "event_status":0,\
    "info": "3",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "4",\
    "time": "20180404095212",\
    "version": "1.0"\
    }')
    CommunicationTerminal.typicalSend(de, ReplyTaskStatus.GRASPING)
