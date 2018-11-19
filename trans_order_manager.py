import utils
import accepts
# from urllib import request
import requests
from trans_order import TransportOrder
from order_sequence import OrderSequence
from order_sequence_head import OrderSequenceHead
from order_task import OrderTask

import threading

class TransportOrderManager(object):

    def __init__(self, serverIP = "127.0.0.1", serverPort = 55200, logname = 'order manager'):
        '''
        instructor
        '''
        # _log & _lock must be defined for the decorator mb_lock_and_catch
        self._log = utils.logger().getLogger(logname)
        self._lock = threading.Lock()
        self._reqPath = 'http://%s:%d/v1/' % (serverIP, serverPort)
        self._reqOrderPath = self._reqPath + 'transportOrders/'
        self._reqVehiclePath = self._reqPath + 'vehicles/'
        self._reqSequencePath = self._reqPath + 'orderSequence/'
        self._reqTaskPath = self._reqPath + 'orderTask/'


    @utils.mb_lock_and_catch
    @accepts.mb_accepts(TransportOrder, str)
    def sendOrder(self, tOrder, orderName = 'undefine-order'):
        '''
        send order with specified name. need instruct an order first
        '''
        reqUri = self._reqOrderPath + orderName
        postData = tOrder.encode().encode('utf-8')
        self._log.info(reqUri)
        self._log.info(postData)
        # req = request.Request(url = reqUri, data = postData, method = 'POST')
        # r = request.urlopen(req).read()
        # self._log.info(r.decode('utf-8'))
        req = requests.post(url = reqUri, data = postData)
        self._log.info('code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))

    @utils.mb_lock_and_catch
    @accepts.mb_accepts(OrderSequence, str)
    def sendOrderSequence(self, os, sequenceName = 'undefine-sequence'):
        '''
        send order sequence with specified name.
        '''
        reqUri = self._reqSequencePath + sequenceName
        postData = os.encode().encode('utf-8')
        self._log.info(reqUri)
        self._log.info(postData)
        # req = request.Request(url = reqUri, data = postData, method = 'POST')
        # r = request.urlopen(req).read()
        # self._log.info(r.decode('utf-8'))
        req = requests.post(url = reqUri, data = postData)
        self._log.info('code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))

    @utils.mb_lock_and_catch
    @accepts.mb_accepts(OrderTask)
    def sendOrderTask(self, ot):
        '''
        send order task with specified name.
        '''
        reqUri = self._reqTaskPath + ot.getName()
        postData = ot.encode().encode('utf-8')
        self._log.info(reqUri)
        self._log.info(postData)
        # req = request.Request(url = reqUri, data = postData, method = 'POST')
        # r = request.urlopen(req).read()
        # self._log.info(r.decode('utf-8'))
        req = requests.post(url = reqUri, data = postData)
        self._log.info('code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))
        
    @utils.mb_lock_and_catch
    @accepts.mb_accepts(str, bool, bool)
    def withdrawOrderByName(self, orderName = 'undefine-order', immediate = False, disableVehicle = False):
        reqUri = self._reqOrderPath + orderName + '/withdrawal'
        reqParam = '?immediate=%s&disableVehicle=%s' % (str(immediate).lower(), str(disableVehicle).lower())
        reqUri = reqUri + reqParam
        # print(reqUri)
        # print(postData)
        # req = request.Request(url = reqUri, method = 'POST')
        # r = request.urlopen(req).read()
        # self._log.info(r.decode('utf-8'))
        req = requests.post(url = reqUri)
        self._log.info('code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))


    @utils.mb_lock_and_catch
    @accepts.mb_accepts(str, bool, bool)
    def withdrawOrderByVehicle(self, vehicle = 'undefine-vehicle', immediate = False, disableVehicle = False):
        reqUri = self._reqVehiclePath + vehicle + '/withdrawal'
        reqParam = '?immediate=%s&disableVehicle=%s' % (str(immediate).lower(), str(disableVehicle).lower())
        reqUri = reqUri + reqParam
        # print(reqUri)
        # print(postData)
        # req = request.Request(url = reqUri, method = 'POST')
        # r = request.urlopen(req).read()
        # self._log.info(r.decode('utf-8'))
        req = requests.post(url = reqUri)
        self._log.info('code ' + str(req.status_code) + ' ' + req.content.decode('utf-8'))

    @utils.mb_lock_and_catch
    @accepts.mb_accepts(str)
    def getOrderInfo(self, orderName):
        reqUri = self._reqOrderPath + orderName
        res = requests.get(reqUri)
        return res.json()

if __name__ == '__main__':
    import time
    tm = TransportOrderManager()

    # tm.getOrderInfo('aaa')

    s = OrderSequenceHead()
    s.setCategory('work')
    s.setFailureFatal(False)
    s1 = OrderSequenceHead()
    s1.setCategory('trans')

    t = TransportOrder()
    t.addDestination("Location WL5",'load')

    t1 = TransportOrder()
    t1.addDestination("Location CP4", 'CHARGE')

    t2 = TransportOrder()
    t2.addDestination("Location WL7",'load')

    t3 = TransportOrder()
    t3.addDestination("Location WL12", 'load')
    t4 = TransportOrder()
    t4.addDestination("Location WL6", 'load')
    t5 = TransportOrder()
    t5.addDestination("Location WL10", 'load', TransportOrder.createProterty('bbb','222'))
    t5.addDestination("Location WL10", 'load', TransportOrder.createProterty('ccc','222'))
    t5.addDestination("Location WL10", 'load', TransportOrder.createProterty('ddd','222'))
    t5.addOrderProperties(TransportOrder.createProterty('mmm','111'), TransportOrder.createProterty('ccc','222'))

    task = OrderTask()
    task.setName('laasaa')
    task.addOrderSequenceHead(s)
    task.addOrderSequenceHead(s1)
    task.addTransportOrder(t, 0)
    task.addTransportOrder(t1, 1)
    task.addTransportOrder(t2, 0, 1)
    task.addTransportOrder(t3, 0)
    task.addTransportOrder(t4, 0)
    task.addTransportOrder(t5, 1, 4, 3)

    tm.sendOrderTask(task)
