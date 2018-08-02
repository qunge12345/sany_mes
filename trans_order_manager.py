import utils
import accepts
from urllib import request
from trans_order import TransportOrder
from order_sequence import OrderSequence

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
        req = request.Request(url = reqUri, data = postData, method = 'POST')
        r = request.urlopen(req).read()
        self._log.info(r.decode('utf-8'))

    @utils.mb_lock_and_catch
    @accepts.mb_accepts(OrderSequence, str)
    def sendOrderSequence(self, ts, sequenceName = 'undefine-sequence'):
        '''
        send order sequence with specified name.
        '''
        reqUri = self._reqSequencePath + sequenceName
        postData = ts.encode().encode('utf-8')
        self._log.info(reqUri)
        self._log.info(postData)
        req = request.Request(url = reqUri, data = postData, method = 'POST')
        r = request.urlopen(req).read()
        self._log.info(r.decode('utf-8'))

        
    @utils.mb_lock_and_catch
    @accepts.mb_accepts(str, bool, bool)
    def withdrawOrderByName(self, orderName = 'undefine-order', immediate = False, disableVehicle = False):
        reqUri = self._reqOrderPath + orderName + '/withdrawal'
        reqParam = '?immediate=%s&disableVehicle=%s' % (str(immediate).lower(), str(disableVehicle).lower())
        reqUri = reqUri + reqParam
        # print(reqUri)
        # print(postData)
        req = request.Request(url = reqUri, method = 'POST')
        r = request.urlopen(req).read()
        self._log.info(r.decode('utf-8'))


    @utils.mb_lock_and_catch
    @accepts.mb_accepts(str, bool, bool)
    def withdrawOrderByVehicle(self, vehicle = 'undefine-vehicle', immediate = False, disableVehicle = False):
        reqUri = self._reqVehiclePath + vehicle + '/withdrawal'
        reqParam = '?immediate=%s&disableVehicle=%s' % (str(immediate).lower(), str(disableVehicle).lower())
        reqUri = reqUri + reqParam
        # print(reqUri)
        # print(postData)
        req = request.Request(url = reqUri, method = 'POST')
        r = request.urlopen(req).read()
        self._log.info(r.decode('utf-8'))

    


if __name__ == '__main__':
    import time
    tm = TransportOrderManager()
    # t = TransportOrder()
    # t.setDeadline()
    # t.addDestination("Location-0001","load")
    # # tm.sendOrder(t, "TOrder-0008")
    # tm.withdrawOrderByVehicle(immediate=True)
    t = TransportOrder()
    t.addDestination("Location WL28","work")
    t.addDestination("Location WL29","work")

    time.sleep(1)
    t1 = TransportOrder()
    t1.addDestination("Location WL30","work")
    t1.addDestination("Location WL31","work")
    # t1.addOrderDependencies('pppppppppp', 'ssssssssssss')

    s = OrderSequence()
    s.addTransportOrder(t)
    s.addTransportOrder(t1)
    s.setCategory('-')

    s.setFailureFatal(False)
    # tm.sendOrder(t)
    tm.sendOrderSequence(s, 'hehe2')

