import socket
import threading
import time
import datetime
import os
import json

import utils
from trans_order import TransportOrder
from trans_order_manager import TransportOrderManager

# global define
vehicle_1 = 'AMB-300-1808-06'
vehicle_2 = 'AMB-300-1808-07'
vehicle_3 = 'AMB-300-1808-05'
vehicle_4 = 'AMB-300-1808-04'

vehicle_5 = 'AMB-300-1808-02'
vehicle_6 = 'AMB-300-1808-03'

def main():
    log = utils.logger().getLogger('MES-EXPO')
    tom = TransportOrderManager(serverIP = "192.168.0.91", serverPort = 55200)

    def createOrder(loc, op, vehicle, dependency = None):
        torder = TransportOrder()
        prop = {}
        if 'RollerLoad' == op:
            prop = TransportOrder.createProterty('direction', 'left')
        elif 'RollerUnload' == op:
            prop = TransportOrder.createProterty('direction', 'right')
        else:
            pass
        props = (prop,)
        torder.addDestination(loc, op, *props)
        torder.setIntendedVehicle(vehicle)
        if dependency:
            if isinstance(dependency, str):
                torder.addOrderDependencies(dependency)
            elif isinstance(dependency, tuple):
                torder.addOrderDependencies(*dependency)
        torder.setDeadline(datetime.datetime.now())
        return torder

    def getNewOrderName(order):
        vehicle = order.getOrder().get('intendedVehicle')
        loc = order.getOrder().get('destinations')[0].get('locationName')
        operation = order.getOrder().get('destinations')[0].get('operation')
        return '%s_%s_%s_at_%s' % (vehicle, loc, operation, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f'))


    # first order
    o1 = createOrder('L1B', 'wait', vehicle_1)
    name1 = getNewOrderName(o1)
    tom.sendOrder(o1, name1)
    time.sleep(0.2)

    o2 = createOrder('L2A', 'wait', vehicle_2)
    name2 = getNewOrderName(o2)
    tom.sendOrder(o2, name2)
    time.sleep(0.2)

    o3 = createOrder('L3B', 'wait', vehicle_3)
    name3 = getNewOrderName(o3)
    tom.sendOrder(o3, name3)
    time.sleep(0.2)

    o4 = createOrder('L4A', 'wait', vehicle_4)
    name4 = getNewOrderName(o4)
    tom.sendOrder(o4, name4)
    time.sleep(0.2)

    o1b = createOrder('L1B', 'RollerLoad', vehicle_1, (name2,name1))
    name1b = getNewOrderName(o1b)
    tom.sendOrder(o1b, name1b)
    time.sleep(0.2)

    o2b = createOrder('L2A', 'RollerUnload', vehicle_2, (name1,name2))
    name2b = getNewOrderName(o2b)
    tom.sendOrder(o2b, name2b)
    time.sleep(0.2)

    o3b = createOrder('L3B', 'RollerLoad', vehicle_3, (name4,name3))
    name3b = getNewOrderName(o3b)
    tom.sendOrder(o3b, name3b)
    time.sleep(0.2)

    o4b = createOrder('L4A', 'RollerUnload', vehicle_4, (name3,name4))
    name4b = getNewOrderName(o4b)
    tom.sendOrder(o4b, name4b)
    time.sleep(0.2)

    o5 = createOrder('L5A', 'wait', vehicle_5)
    tom.sendOrder(o5, getNewOrderName(o5))
    time.sleep(0.2)

    o6 = createOrder('L6A', 'wait', vehicle_6)
    tom.sendOrder(o6, getNewOrderName(o6))
    time.sleep(0.2)

    o5 = createOrder('L5B', 'wait', vehicle_5)
    tom.sendOrder(o5, getNewOrderName(o5))
    time.sleep(0.2)

    o6 = createOrder('L6B', 'wait', vehicle_6)
    tom.sendOrder(o6, getNewOrderName(o6))
    time.sleep(0.2)

    # second order
    o1 = createOrder('L1A', 'wait', vehicle_1, name1b)
    name1 = getNewOrderName(o1)
    tom.sendOrder(o1, name1)
    time.sleep(0.2)

    o4 = createOrder('L4B', 'wait', vehicle_4, (name3b, name4b))
    name4 = getNewOrderName(o4)
    tom.sendOrder(o4, name4)
    time.sleep(0.2)

    o3 = createOrder('L3A', 'wait', vehicle_3, name3b)
    name3 = getNewOrderName(o3)
    tom.sendOrder(o3, name3)
    time.sleep(0.2)

    o2 = createOrder('L2B', 'wait', vehicle_2, (name1b, name2b))
    name2 = getNewOrderName(o2)
    tom.sendOrder(o2, name2)
    time.sleep(0.2)

    o1b = createOrder('L1A', 'RollerUnload', vehicle_1, (name4,name1))
    name1b = getNewOrderName(o1b)
    tom.sendOrder(o1b, name1b)
    time.sleep(0.2)

    o4b = createOrder('L4B', 'RollerLoad', vehicle_4, (name1,name4))
    name4b = getNewOrderName(o4b)
    tom.sendOrder(o4b, name4b)
    time.sleep(0.2)


    o3b = createOrder('L3A', 'RollerUnload', vehicle_3, (name2,name3))
    name3b = getNewOrderName(o3b)
    tom.sendOrder(o3b, name3b)
    time.sleep(0.2)

    o2b = createOrder('L2B', 'RollerLoad', vehicle_2, (name3,name2))
    name2b = getNewOrderName(o2b)
    tom.sendOrder(o2b, name2b)
    time.sleep(0.2)

    o5 = createOrder('L5A', 'wait', vehicle_5)
    tom.sendOrder(o5, getNewOrderName(o5))
    time.sleep(0.2)

    o6 = createOrder('L6A', 'wait', vehicle_6)
    tom.sendOrder(o6, getNewOrderName(o6))
    time.sleep(0.2)

    o5 = createOrder('L5B', 'wait', vehicle_5)
    tom.sendOrder(o5, getNewOrderName(o5))
    time.sleep(0.2)

    o6 = createOrder('L6B', 'wait', vehicle_6)
    tom.sendOrder(o6, getNewOrderName(o6))
    time.sleep(0.2)


    time.sleep(20)

    while True:

        # first order
        o1 = createOrder('L1B', 'wait', vehicle_1, (name4b,name1b))
        name1 = getNewOrderName(o1)
        tom.sendOrder(o1, name1)
        time.sleep(0.2)

        o2 = createOrder('L2A', 'wait', vehicle_2, name2b)
        name2 = getNewOrderName(o2)
        tom.sendOrder(o2, name2)
        time.sleep(0.2)

        o3 = createOrder('L3B', 'wait', vehicle_3, (name2b,name3b))
        name3 = getNewOrderName(o3)
        tom.sendOrder(o3, name3)
        time.sleep(0.2)

        o4 = createOrder('L4A', 'wait', vehicle_4, name4b)
        name4 = getNewOrderName(o4)
        tom.sendOrder(o4, name4)
        time.sleep(0.2)

        o1b = createOrder('L1B', 'RollerLoad', vehicle_1, (name2,name1))
        name1b = getNewOrderName(o1b)
        tom.sendOrder(o1b, name1b)
        time.sleep(0.2)

        o2b = createOrder('L2A', 'RollerUnload', vehicle_2, (name1,name2))
        name2b = getNewOrderName(o2b)
        tom.sendOrder(o2b, name2b)
        time.sleep(0.2)

        o3b = createOrder('L3B', 'RollerLoad', vehicle_3, (name4,name3))
        name3b = getNewOrderName(o3b)
        tom.sendOrder(o3b, name3b)
        time.sleep(0.2)

        o4b = createOrder('L4A', 'RollerUnload', vehicle_4, (name3,name4))
        name4b = getNewOrderName(o4b)
        tom.sendOrder(o4b, name4b)
        time.sleep(0.2)

        o5 = createOrder('L5A', 'wait', vehicle_5)
        tom.sendOrder(o5, getNewOrderName(o5))
        time.sleep(0.2)

        o6 = createOrder('L6A', 'wait', vehicle_6)
        tom.sendOrder(o6, getNewOrderName(o6))
        time.sleep(0.2)

        o5 = createOrder('L5B', 'wait', vehicle_5)
        tom.sendOrder(o5, getNewOrderName(o5))
        time.sleep(0.2)

        o6 = createOrder('L6B', 'wait', vehicle_6)
        tom.sendOrder(o6, getNewOrderName(o6))
        time.sleep(0.2)

        # second order
        o1 = createOrder('L1A', 'wait', vehicle_1, name1b)
        name1 = getNewOrderName(o1)
        tom.sendOrder(o1, name1)
        time.sleep(0.2)

        o4 = createOrder('L4B', 'wait', vehicle_4, (name3b,name4b))
        name4 = getNewOrderName(o4)
        tom.sendOrder(o4, name4)
        time.sleep(0.2)

        o3 = createOrder('L3A', 'wait', vehicle_3, name3b)
        name3 = getNewOrderName(o3)
        tom.sendOrder(o3, name3)
        time.sleep(0.2)

        o2 = createOrder('L2B', 'wait', vehicle_2, (name1b,name2b))
        name2 = getNewOrderName(o2)
        tom.sendOrder(o2, name2)
        time.sleep(0.2)

        o1b = createOrder('L1A', 'RollerUnload', vehicle_1, (name4,name1))
        name1b = getNewOrderName(o1b)
        tom.sendOrder(o1b, name1b)
        time.sleep(0.2)

        o4b = createOrder('L4B', 'RollerLoad', vehicle_4, (name1,name4))
        name4b = getNewOrderName(o4b)
        tom.sendOrder(o4b, name4b)
        time.sleep(0.2)

        o3b = createOrder('L3A', 'RollerUnload', vehicle_3, (name2,name3))
        name3b = getNewOrderName(o3b)
        tom.sendOrder(o3b, name3b)
        time.sleep(0.2)

        o2b = createOrder('L2B', 'RollerLoad', vehicle_2, (name3,name2))
        name2b = getNewOrderName(o2b)
        tom.sendOrder(o2b, name2b)
        time.sleep(0.2)

        o5 = createOrder('L5A', 'wait', vehicle_5)
        tom.sendOrder(o5, getNewOrderName(o5))
        time.sleep(0.2)

        o6 = createOrder('L6A', 'wait', vehicle_6)
        tom.sendOrder(o6, getNewOrderName(o6))
        time.sleep(0.2)

        o5 = createOrder('L5B', 'wait', vehicle_5)
        tom.sendOrder(o5, getNewOrderName(o5))
        time.sleep(0.2)

        o6 = createOrder('L6B', 'wait', vehicle_6)
        tom.sendOrder(o6, getNewOrderName(o6))
        time.sleep(0.2)

        time.sleep(20)
        
        


if __name__ == '__main__':
    main()