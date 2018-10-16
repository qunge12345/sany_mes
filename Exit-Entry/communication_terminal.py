
import sys
sys.path.append("..")

import utils
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from event_processor import EventProcessor
import threading
from ctypes import *

class CommunicationTerminal(BaseHTTPRequestHandler):
    '''
    communicate with XiongDi devices
    '''
    @staticmethod
    def initialize(eventProcessor, loggerName = 'communication terminal'):
        CommunicationTerminal.log = utils.logger().getLogger(loggerName)
        CommunicationTerminal.evtProc = eventProcessor
        soaplib = cdll.LoadLibrary("./GSoapDll.dll")

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
    def typicalSend(evt, success = True):
        # data = rb'{"data":"{\"event_id\":\"%s\",\"event_info\":\"%s\",\"event_status\":\"%s\",\"machine_code\":\"%s\",\"machine_ip\":\"%s\"}","id" :"","type" : "%s"}' % \
        # (evt.getMachineStatus(), )
        CommunicationTerminal.log.info(evt.getMachineName() + '_' + evt.getType().name + ' operate ' + success)


if __name__ == '__main__':
    # import time
    # CommunicationTerminal.initialize("i'm wrong")
    # CommunicationTerminal.startServer()
    # while True:
    #     time.sleep(1)
    m = 222
    t = rb'{"data":"{\"event_id\":\"%s\",\"event_info\":\"\",\"ip\":\"192.168.1.12\"}","id" :"","type" : "1"}' % str(m).encode('utf-8')
    print(t)
