import socket
import threading
import time
import datetime
import os
import json
import redis

import utils
from trans_order import TransportOrder
from trans_order_manager import TransportOrderManager



def main():
    log = utils.logger().getLogger('MES')
    conFile = os.path.abspath(os.path.join(os.getcwd(), 'config.json'))
    conf = {}
    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)
    r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)

    # get config file
    try:          
        with open(conFile, 'r') as f:
            conf = json.load(f)
    except:
        with open(conFile, 'a') as f:
            log.critical('%s is illegal' % conFile)
            f.write('\n******************check ERROR in this file, then delete this line******************')
    

    # tcp client thread:
    def clientThread(serverIP, serverPort):
        myconf = conf.copy()
        thisConf = [x for x in myconf.get('servers',[]) if x.get('ip') == serverIP and x.get('port') == serverPort][0]
        startLoc = thisConf.get('location')
        is_emc = thisConf.get('is_emergency')
        while True:            
            try:
                tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                log.info('socket---%s' % tcpClientSocket)
                tcpClientSocket.connect((serverIP, serverPort))
                while True:
                    recvData = tcpClientSocket.recv(15)
                    log.info(serverIP + " receive matrix key: " + str(recvData))
                    try:
                        recvStr = recvData.decode('utf-8')[:8]
                    except Exception as e:
                        # receive first responce
                        log.error('decode failed ' + str(e))
                        continue
                    destList = [x for x in myconf.get('matrix_data',[]) if x.get('key') == recvStr]
                    dest = destList[0] if len(destList) > 0 else None
                    if dest is not None:
                        torder = TransportOrder()
                        torder.addDestination(location = startLoc, operation = 'load')
                        if dest.get('fullP') != '':
                            torder.addDestination(location = dest.get('fullP'), operation = 'unload')
                            if dest.get('emptyP') != '':
                                torder.addDestination(location = dest.get('emptyP'), operation = 'see')
                        else:
                            torder.addDestination(location = conf.get('basket_home'), operation = 'drop')
                            
                        if True == is_emc:
                            torder.setDeadline(datetime.datetime.now())
                        tom.sendOrder(torder, ('established_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))

            except Exception as e:
                log.error(str(e) + serverIP + ":" + str(serverPort))
            finally:
                tcpClientSocket.close()
                time.sleep(5)


    # run listening
    for server in conf.get("servers",[]):
        serverAddr = (server.get('ip'), server.get('port'))
        mt = threading.Thread(target = clientThread, name = 'client %s:%d' % serverAddr , args = serverAddr)
        mt.setDaemon(True)
        mt.start()

    # for special work
    locHome = conf.get('basket_home')
    if not isinstance(locHome, list):
        log.error('basket_home is not a location list but ' + str(type(locHome)))        
    p = r.pubsub()
    p.subscribe("TAKE_BASKET_HOME")    

    for item in p.listen():
        bmsg = item.get('data',b'')
        if isinstance(bmsg, bytes) and item.get('channel',b'') == b'TAKE_BASKET_HOME': 
            msg = json.loads(bmsg.decode()) 
            loc = 'L' + msg.get('location')[2:]
            torder = TransportOrder()
            torder.addDestination(location = loc, operation = 'load')
            if 'Vehicle-01' == msg.get('vehicle'):
                torder.addDestination(location = locHome[0], operation = 'drop')
            elif 'Vehicle-02' == msg.get('vehicle'):
                torder.addDestination(location = locHome[1], operation = 'drop')                
            torder.setIntendedVehicle(msg.get('vehicle'))
            torder.setDeadline(datetime.datetime.now() - datetime.timedelta(hours = 1))
            tom.sendOrder(torder, ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))

    # sleep
    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()