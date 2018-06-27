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
    log = utils.logger().getLogger('MES-WODI')
    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

    def createOrder(loc1 = '', loc2 = ''):
        torder = TransportOrder()
        torder.addDestination(location = loc1, operation = 'load')
        torder.addDestination(location = loc2, operation = 'unload')
        torder.setDeadline(datetime.datetime.now())
        return torder

    while True:
        
        tom.sendOrder(createOrder('L1','L4'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        time.sleep(2)
        tom.sendOrder(createOrder('L2','L5'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        time.sleep(2)
        tom.sendOrder(createOrder('L3','L6'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        
        time.sleep(60)
        
        tom.sendOrder(createOrder('L4','L1'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        time.sleep(2)
        tom.sendOrder(createOrder('L5','L2'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        time.sleep(2)
        tom.sendOrder(createOrder('L6','L3'), ('take_home_at_%s' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))

        time.sleep(60)
        


if __name__ == '__main__':
    main()