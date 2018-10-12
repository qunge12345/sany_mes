
import sys
sys.path.append('..')

from vehicle import *
from xd_event import *
from vehicle_manager import *
from slot_adapter import *

import utils
import json
import time
import datetime
import threading

from trans_order import TransportOrder
from order_sequence_head import OrderSequenceHead
from order_task import OrderTask
from trans_order_manager import TransportOrderManager

class TaskManager(object):

    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

    @staticmethod
    def createNormalTask(evt, vehicle):
        '''
        create a thread of normal task
        '''
        nt = threading.Thread(target = TaskManager.normalTask, name = 'normal_task_at_%s' % evt.getMachineName(), args = (evt, vehicle))
        nt.setDaemon(True)
        nt.start()

    @staticmethod
    def createReloadTask(vehicle):
        '''
        create a thread of reload task
        '''
        rt = threading.Thread(target = TaskManager.reloadTask, name = 'reload_task_at_%s' % vehicle.getName(), args = (vehicle,))
        rt.setDaemon(True)
        rt.start()

    @staticmethod
    def normalTask(evt, vehicle):
        '''
        a normal task to load or unload
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)

    @staticmethod
    def reloadTask(vehicle):
        '''
        go to reload

        TODO: use config file instead of those string !!!
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)

        # confirm the location
        location = 'Location_Unload'
        if vehicle.getType() in (VehicleType.XD_LOADER, VehicleType.HX_LOADER):
            location = 'Location_Load'

        t = TransportOrder()
        t.setIntendedVehicle(vehicle)
        prop = TransportOrder.createProterty('duration', '5000')
        t.addDestination(location, 'Wait', *(prop,))
        name = 'reload_' + vehicle.getName() + '_' + datetime.datetime.now()
        tom.sendOrder(t, name)

        # wait for executing
        time.sleep(10)

        while False == TaskManager.isOrderFinished(name):
            time.sleep(5)

        vehicle.setStatus(VehicleStatus.IDLE)

    @staticmethod
    def isOrderFinished(orderName):
        '''
        return True if order is finished
        '''
        orderStatus = tom.getOrderInfo(orderName)['state']
        return orderStatus in ('FINISHED', 'FAILED')

    @staticmethod
    def isOrderTaskFinished(orderTask):
        '''
        return True if order task is finished
        '''
        orderStatus = tom.getOrderInfo(orderTask.getOrderNameByIndex(orderTask.getOrdersNum() - 1))['state']
        return orderStatus in ('FINISHED', 'FAILED')

if __name__ == '__main__':
