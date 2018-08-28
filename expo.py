import socket
import threading
import time
import datetime
import os
import json

import utils
from trans_order import TransportOrder
from trans_order_manager import TransportOrderManager



def main():
    log = utils.logger().getLogger('MES-EXPO')
    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

    def createOrder(loc, op, vehicle, dependency = None):
        torder = TransportOrder()
        torder.addDestination(location = loc, operation = op)
        torder.setIntendedVehicle(vehicle)
        if dependency:
            torder.addOrderDependencies(dependency)
        torder.setDeadline(datetime.datetime.now())
        return torder

    def getNewOrderName():
        return 'take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f')


    # first order
    o1 = createOrder('L1A', 'wait', 'AMB-01')
    name1 = getNewOrderName()
    tom.sendOrder(o1, name1)
    time.sleep(0.2)

    o2 = createOrder('L2A', 'wait', 'AMB-02')
    name2 = getNewOrderName()
    tom.sendOrder(o2, name2)
    time.sleep(0.2)

    o3 = createOrder('L3B', 'wait', 'AMB-03')
    name3 = getNewOrderName()
    tom.sendOrder(o3, name3)
    time.sleep(0.2)

    o4 = createOrder('L4A', 'wait', 'AMB-04')
    name4 = getNewOrderName()
    tom.sendOrder(o4, name4)
    time.sleep(0.2)

    o1b = createOrder('L1A', 'load', 'AMB-01', name2)
    name1b = getNewOrderName()
    tom.sendOrder(o1b, name1b)
    time.sleep(0.2)

    o2b = createOrder('L2A', 'unload', 'AMB-02', name1)
    name2b = getNewOrderName()
    tom.sendOrder(o2b, name2b)
    time.sleep(0.2)

    o3b = createOrder('L3B', 'load', 'AMB-03', name4)
    name3b = getNewOrderName()
    tom.sendOrder(o3b, name3b)
    time.sleep(0.2)

    o4b = createOrder('L4A', 'unload', 'AMB-04', name3)
    name4b = getNewOrderName()
    tom.sendOrder(o4b, name4b)
    time.sleep(0.2)

    o5 = createOrder('L5A', 'wait', 'AMB-05')
    tom.sendOrder(o5, getNewOrderName())
    time.sleep(0.2)

    o6 = createOrder('L6A', 'wait', 'AMB-06')
    tom.sendOrder(o6, getNewOrderName())
    time.sleep(0.2)

    o5 = createOrder('L5B', 'wait', 'AMB-05')
    tom.sendOrder(o5, getNewOrderName())
    time.sleep(0.2)

    o6 = createOrder('L6B', 'wait', 'AMB-06')
    tom.sendOrder(o6, getNewOrderName())
    time.sleep(0.2)




    # second order
    o1 = createOrder('L1B', 'wait', 'AMB-01', name1b)
    name1 = getNewOrderName()
    tom.sendOrder(o1, name1)
    time.sleep(0.2)

    o4 = createOrder('L4B', 'wait', 'AMB-04', name3b)
    name4 = getNewOrderName()
    tom.sendOrder(o4, name4)
    time.sleep(0.2)

    o3 = createOrder('L3A', 'wait', 'AMB-03', name3b)
    name3 = getNewOrderName()
    tom.sendOrder(o3, name3)
    time.sleep(0.2)

    o2 = createOrder('L2B', 'wait', 'AMB-02', name1b)
    name2 = getNewOrderName()
    tom.sendOrder(o2, name2)
    time.sleep(0.2)

    o1b = createOrder('L1B', 'unload', 'AMB-01', name4)
    name1b = getNewOrderName()
    tom.sendOrder(o1b, name1b)
    time.sleep(0.2)

    o4b = createOrder('L4B', 'load', 'AMB-04', name1)
    name4b = getNewOrderName()
    tom.sendOrder(o4b, name4b)
    time.sleep(0.2)


    o3b = createOrder('L3A', 'unload', 'AMB-03', name2)
    name3b = getNewOrderName()
    tom.sendOrder(o3b, name3b)
    time.sleep(0.2)

    o2b = createOrder('L2B', 'load', 'AMB-02', name3)
    name2b = getNewOrderName()
    tom.sendOrder(o2b, name2b)
    time.sleep(0.2)

    o5 = createOrder('L5A', 'wait', 'AMB-05')
    tom.sendOrder(o5, getNewOrderName())
    time.sleep(0.2)

    o6 = createOrder('L6A', 'wait', 'AMB-06')
    tom.sendOrder(o6, getNewOrderName())
    time.sleep(0.2)

    o5 = createOrder('L5B', 'wait', 'AMB-05')
    tom.sendOrder(o5, getNewOrderName())
    time.sleep(0.2)

    o6 = createOrder('L6B', 'wait', 'AMB-06')
    tom.sendOrder(o6, getNewOrderName())
    time.sleep(0.2)

    time.sleep(60)

    while True:

        # first order
        o1 = createOrder('L1A', 'wait', 'AMB-01', name4b)
        name1 = getNewOrderName()
        tom.sendOrder(o1, name1)
        time.sleep(0.2)

        o2 = createOrder('L2A', 'wait', 'AMB-02', name2b)
        name2 = getNewOrderName()
        tom.sendOrder(o2, name2)
        time.sleep(0.2)

        o3 = createOrder('L3B', 'wait', 'AMB-03', name2b)
        name3 = getNewOrderName()
        tom.sendOrder(o3, name3)
        time.sleep(0.2)

        o4 = createOrder('L4A', 'wait', 'AMB-04', name4b)
        name4 = getNewOrderName()
        tom.sendOrder(o4, name4)
        time.sleep(0.2)

        o1b = createOrder('L1A', 'load', 'AMB-01', name2)
        name1b = getNewOrderName()
        tom.sendOrder(o1b, name1b)
        time.sleep(0.2)

        o2b = createOrder('L2A', 'unload', 'AMB-02', name1)
        name2b = getNewOrderName()
        tom.sendOrder(o2b, name2b)
        time.sleep(0.2)

        o3b = createOrder('L3B', 'load', 'AMB-03', name4)
        name3b = getNewOrderName()
        tom.sendOrder(o3b, name3b)
        time.sleep(0.2)

        o4b = createOrder('L4A', 'unload', 'AMB-04', name3)
        name4b = getNewOrderName()
        tom.sendOrder(o4b, name4b)
        time.sleep(0.2)

        o5 = createOrder('L5A', 'wait', 'AMB-05')
        tom.sendOrder(o5, getNewOrderName())
        time.sleep(0.2)

        o6 = createOrder('L6A', 'wait', 'AMB-06')
        tom.sendOrder(o6, getNewOrderName())
        time.sleep(0.2)

        o5 = createOrder('L5B', 'wait', 'AMB-05')
        tom.sendOrder(o5, getNewOrderName())
        time.sleep(0.2)

        o6 = createOrder('L6B', 'wait', 'AMB-06')
        tom.sendOrder(o6, getNewOrderName())
        time.sleep(0.2)




        # second order
        o1 = createOrder('L1B', 'wait', 'AMB-01', name1b)
        name1 = getNewOrderName()
        tom.sendOrder(o1, name1)
        time.sleep(0.2)

        o4 = createOrder('L4B', 'wait', 'AMB-04', name3b)
        name4 = getNewOrderName()
        tom.sendOrder(o4, name4)
        time.sleep(0.2)

        o3 = createOrder('L3A', 'wait', 'AMB-03', name3b)
        name3 = getNewOrderName()
        tom.sendOrder(o3, name3)
        time.sleep(0.2)

        o2 = createOrder('L2B', 'wait', 'AMB-02', name1b)
        name2 = getNewOrderName()
        tom.sendOrder(o2, name2)
        time.sleep(0.2)

        o1b = createOrder('L1B', 'unload', 'AMB-01', name4)
        name1b = getNewOrderName()
        tom.sendOrder(o1b, name1b)
        time.sleep(0.2)

        o4b = createOrder('L4B', 'load', 'AMB-04', name1)
        name4b = getNewOrderName()
        tom.sendOrder(o4b, name4b)
        time.sleep(0.2)

        o3b = createOrder('L3A', 'unload', 'AMB-03', name2)
        name3b = getNewOrderName()
        tom.sendOrder(o3b, name3b)
        time.sleep(0.2)

        o2b = createOrder('L2B', 'load', 'AMB-02', name3)
        name2b = getNewOrderName()
        tom.sendOrder(o2b, name2b)
        time.sleep(0.2)

        o5 = createOrder('L5A', 'wait', 'AMB-05')
        tom.sendOrder(o5, getNewOrderName())
        time.sleep(0.2)

        o6 = createOrder('L6A', 'wait', 'AMB-06')
        tom.sendOrder(o6, getNewOrderName())
        time.sleep(0.2)

        o5 = createOrder('L5B', 'wait', 'AMB-05')
        tom.sendOrder(o5, getNewOrderName())
        time.sleep(0.2)

        o6 = createOrder('L6B', 'wait', 'AMB-06')
        tom.sendOrder(o6, getNewOrderName())
        time.sleep(0.2)
        
        time.sleep(60)
        
        


if __name__ == '__main__':
    main()